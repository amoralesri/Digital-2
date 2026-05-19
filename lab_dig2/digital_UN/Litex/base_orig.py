#!/usr/bin/env python3

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from litex.gen import *
from litex.build.generic_platform import *
from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect import wishbone

from litex.soc.cores.led import LedChaser

from liteeth.phy.rmii import LiteEthPHYRMII

from board import ecb_t8_t113



# PSRAM flash emulation ----------------------------------------------------------------------------------------------

from litespi.spi_nor_flash_module import SpiNorFlashModule
from litespi.opcodes import SpiNorFlashOpCodes as Codes

from rtl.spi_ram import SpiRamQuad
from rtl.spi_ram_dual import SpiRamDualQuad


class PSRAM(SpiNorFlashModule):

    manufacturer_id = 0x000d
    device_id = 0x0000
    name = "PSRAM"

    total_size  =    8388608   # bytes
    page_size   =       1024   # bytes
    total_pages =       8192

    supported_opcodes = [
        Codes.READ_1_1_1,
        Codes.READ_1_1_1_FAST,
        Codes.READ_1_4_4,
        Codes.PP_1_1_1,
    ]
    dummy_bits = 8

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        clk33 = platform.request("clk33")
        rst_n = platform.request("user_btn", 0)

        # PLL
        self.pll = pll = TRIONPLL(platform)
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk33, 33.333e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=True)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=99.999e6, 
        with_spi_flash      = False,
        with_led_chaser     = True,
        with_ethernet       = False,
        with_etherbone      = False,
        eth_ip              = "10.42.0.220",
        eth_dynamic_ip      = False, 
        **kwargs):
        platform = ecb_t8_t113.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(
            self, 
            platform, 
            clk_freq                 = sys_clk_freq, 
            ident                    = "LiteX SoC on Efinix Trion T20ECB_T8_T113 Board", 
#            integrated_main_ram_size = 0x8000,
#            integrated_sram_size     = 0x9000,
            **kwargs)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q32JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q32JV(Codes.READ_1_1_1), with_master=True)

        # SPI RAM --------------------------------------------------------------------------------
        #reset_cycles = 2**14-1
#        ram = SpiRamQuad(platform.request("spiram4x", 0), dummy=5, qpi=True)
        ram = SpiRamDualQuad(platform.request("spiram4x", 0), dummy=6, qpi=True)
        self.submodules.ram = ram
        #self.register_mem("main_ram", self.mem_map["main_ram"], self.ram.bus, size=8 * 1024 * 1024)
        self.bus.add_slave("main_ram", ram.bus, SoCRegion(origin=0x40000000, size=8*1024*1024, mode="rw"))

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            from liteeth.phy.rmii import LiteEthPHYRMII
            self.ethphy = LiteEthPHYRMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                refclk_cd  = None
            )
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, software_debug=False )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=ecb_t8_t113.Platform, description="LiteX SoC on Efinix Trion T20 BGA256 Dev Kit.")
    parser.add_target_argument("--flash",          action="store_true",             help="Flash bitstream.")
    parser.add_target_argument("--sys-clk-freq",   default=99.999e6,       type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true",             help="Enable SPI Flash (MMAPed).")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",         action="store_true",    help="Add Ethernet.")
    ethopts.add_argument("--with-etherbone",        action="store_true",    help="Add EtherBone.")
    parser.add_target_argument("--eth-ip",          default="10.42.0.220", help="Etherbone IP address.")
    parser.add_target_argument("--eth-dynamic-ip",  action="store_true",    help="Enable dynamic Ethernet IP addresses setting.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_spi_flash = args.with_spi_flash,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_ip         = args.eth_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
         **parser.soc_argdict)
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("trion_t120_bga576")
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".bit"))

    if args.flash:
        from litex.build.openfpgaloader import OpenFPGALoader
        prog = OpenFPGALoader("trion_t120_bga576")
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".hex")) # FIXME

if __name__ == "__main__":
    main()
