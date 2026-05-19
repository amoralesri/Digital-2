#!/usr/bin/env python3
from migen import *

from litex.gen import *  
from board import tang_primer_25k
from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.clock.gowin_gw5a import GW5APLL



from litex.soc.cores import dna 
from litex.soc.cores.led import LedChaser


platform = tang_primer_25k.Platform() 

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_sdram=False, sdram_rate="1:2"):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        if with_sdram:
            if sdram_rate == "1:2":
                self.cd_sys2x    = ClockDomain()
                self.cd_sys2x_ps = ClockDomain()
            else:
                self.cd_sys_ps = ClockDomain()

        # # #

        # Clk
        clk50 = platform.request("clk50")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += [
            self.cd_por.clk.eq(clk50),
            por_done.eq(por_count == 0),
        ]
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW5APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


# BaseSoC --------------------------------------------------------------------
class BaseSoC(SoCCore): 
    def __init__(self, platform, **kwargs):
        sys_clk_freq = int(50e6)

        # SoC with CPU

        SoCCore.__init__(self, platform, 
            cpu_type                 = "vexriscv",
            clk_freq                 = 50e6,
            ident                    = "LiteX CPU Test on femtoRV", ident_version=True,
            integrated_rom_size      = 0x8000,
            integrated_main_ram_size = 0x4000)
        
        # Clock Reset Generation
        #self.submodules.crg = CRG(platform.request("clk50"), platform.request("user_btn", 0)) 
        self.crg = _CRG(platform, sys_clk_freq)
        # Led
        user_leds = Cat(*[platform.request("user_led", i) for i in range(1)]) 
#        self.submodules.leds = Led(user_leds)
        self.add_csr("leds")   
# Build -----------------------------------------------------------------------
soc = BaseSoC(platform)  
builder = Builder(soc, output_dir="build", csr_csv="csr.csv")
builder.build(build_name="top")