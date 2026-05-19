from migen import *
from migen.genlib.cdc import MultiReg
from litex.soc.interconnect.csr import *
from litex.soc.interconnect.csr_eventmanager import *

class LED_PANEL(Module,AutoCSR):
   def __init__(self, data):
   # Interfaz
    self.clk            = ClockSignal()
    self.rst            = ResetSignal()
    self.init           = CSRStorage()

    self.we_a           = CSRStorage()
    self.mem_w_address  = CSRStorage(12)
    self.mem_w_data     = CSRStorage(24)


    self.LP_CLK         = data.LP_CLK
    self.LATCH          = data.LATCH
    self.NOE            = data.NOE
    self.ROW            = data.ROW
    self.RGB0           = data.RGB0
    self.RGB1           = data.RGB1

    self.specials +=Instance("led_panel_4k", 
        i_clk            = self.clk,
        i_rst            = self.rst,
        i_init           = self.init.storage,
        i_we_a           = self.we_a.storage,
        i_mem_w_address  = self.mem_w_address.storage,
        i_mem_w_data     = self.mem_w_data.storage,
        o_LP_CLK         = self.LP_CLK,
        o_LATCH          = self.LATCH,
        o_NOE            = self.NOE,
        o_ROW            = self.ROW,
        o_RGB0           = self.RGB0,
        o_RGB1           = self.RGB1,
	)	   
    self.submodules.ev = EventManager()
    self.ev.ok = EventSourceProcess()
    self.ev.finalize()
