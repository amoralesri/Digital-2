#!/usr/bin/env python3

from migen import *

from litex.gen import *
from litex_boards.platforms import colorlight_5a_75b
from litex.soc.cores.clock import *
from litex.soc.cores.dma import WishboneDMAReader
from litex.soc.integration.builder import *
from litex.soc.integration.soc_core import *
from litex.soc.interconnect import wishbone
from litex.build.generic_platform import Subsignal, Pins, IOStandard

from litedram.modules import EM636165, M12L16161A, M12L64322A
from litedram.phy import GENSDRPHY, HalfRateGENSDRPHY

from mult import mult_32
from ws2812 import ws2812_streamer

import os


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False, with_rst=False, sdram_rate="1:1"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        if sdram_rate == "1:2":
            self.cd_sys2x    = ClockDomain()
            self.cd_sys2x_ps = ClockDomain()
        else:
            self.cd_sys_ps = ClockDomain()

        if use_internal_osc:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG", p_DIV=div, o_OSC=clk)
            clk_freq = 310e6/div
        else:
            clk = platform.request("clk25")
            clk_freq = 25e6

        rst_n = 1
        if with_rst:
            rst_n = platform.request("user_btn_n", 0)

        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        if sdram_rate == "1:2":
            pll.create_clkout(self.cd_sys2x,    2*sys_clk_freq)
            pll.create_clkout(self.cd_sys2x_ps, 2*sys_clk_freq, phase=180)
        else:
            pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=180)


class BaseSoC(SoCCore):
    def __init__(self, revision="7.0", toolchain="trellis", sys_clk_freq=60e6,
        ws2812_pin=None,
        use_internal_osc=False,
        sdram_rate="1:1",
        **kwargs):

        if ws2812_pin is None:
            raise ValueError("ws2812_pin is required. Pass a package pin like F3 or a connector pin like j1:0.")

        platform = colorlight_5a_75b.Platform(revision=revision, toolchain=toolchain)
        platform.add_extension([
            ("ws2812", 0,
                Subsignal("dout", Pins(ws2812_pin)),
                IOStandard("LVCMOS33"),
            ),
        ])

        uart_name = kwargs.get("uart_name", "serial")
        with_rst = uart_name not in ["serial", "crossover"]
        self.crg = _CRG(platform, sys_clk_freq,
            use_internal_osc=use_internal_osc,
            with_rst=with_rst,
            sdram_rate=sdram_rate,
        )

        kwargs.pop("integrated_rom_size", None)
        kwargs.pop("integrated_rom_init", None)
        kwargs["integrated_rom_size"] = 0x10000
        kwargs["cpu_reset_address"]   = 0x00000000
        if not kwargs.get("integrated_main_ram_size", 0):
            kwargs["integrated_main_ram_size"] = 0x2000

        rom_bin = "NO_bios_fw_dma/firmware.bin"
        if os.path.exists(rom_bin):
            kwargs["integrated_rom_init"] = rom_bin

        SoCCore.__init__(self, platform, int(sys_clk_freq),
            ident=f"LiteX WS2812 DMA on Colorlight 5A-75B rev {revision}",
            **kwargs)

        self.csr.add("mult0")
        self.submodules.mult0 = mult_32.Mult32(platform)

        self.csr.add("disp0")
        self.submodules.disp0 = ws2812_streamer.WS2812(
            platform,
            platform.request("ws2812", 0),
            n_leds=64,
        )

        ws2812_dma_bus = wishbone.Interface(
            data_width=self.bus.data_width,
            adr_width=self.bus.get_address_width(standard="wishbone"),
            addressing="word",
        )
        self.submodules.disp0_dma = WishboneDMAReader(ws2812_dma_bus, with_csr=True)
        self.bus.add_master("disp0_dma", master=ws2812_dma_bus)
        self.csr.add("disp0_dma")
        self.comb += self.disp0_dma.source.connect(self.disp0.sink)

        if not self.integrated_main_ram_size:
            sdrphy_cls = HalfRateGENSDRPHY if sdram_rate == "1:2" else GENSDRPHY
            self.sdrphy = sdrphy_cls(platform.request("sdram"), sys_clk_freq)
            if revision == "6.1":
                sdram_cls = EM636165
            elif revision in ["8.0", "8.2"]:
                sdram_cls = M12L64322A
            else:
                sdram_cls = M12L16161A
            self.add_sdram("sdram",
                phy=self.sdrphy,
                module=sdram_cls(sys_clk_freq, sdram_rate),
                l2_cache_size=kwargs.get("l2_size", 8192),
                l2_cache_full_memory_we=False,
            )


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(
        platform=colorlight_5a_75b.Platform,
        description="LiteX WS2812 DMA SoC on Colorlight 5A-75B.")
    parser.add_target_argument("--revision", default="7.0",
        help="Board revision: 6.1, 7.0, 8.0 or 8.2.")
    parser.add_target_argument("--sys-clk-freq", default=60e6, type=float,
        help="System clock frequency.")
    parser.add_target_argument("--ws2812-pin", required=True,
        help="WS2812 DIN FPGA pin, for example F3 or connector notation j1:0.")
    parser.add_target_argument("--use-internal-osc", action="store_true",
        help="Use internal oscillator instead of clk25.")
    parser.add_target_argument("--sdram-rate", default="1:1",
        help="SDRAM rate if external SDRAM is enabled.")
    args = parser.parse_args()

    soc = BaseSoC(
        revision=args.revision,
        sys_clk_freq=args.sys_clk_freq,
        toolchain=args.toolchain,
        ws2812_pin=args.ws2812_pin,
        use_internal_osc=args.use_internal_osc,
        sdram_rate=args.sdram_rate,
        **parser.soc_argdict
    )

    builder_kwargs = parser.builder_argdict
    if not builder_kwargs.get("output_dir"):
        builder_kwargs["output_dir"] = "build/colorlight_5a_75b_ws2812"
    builder = Builder(soc, **builder_kwargs)

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
