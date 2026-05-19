#!/usr/bin/env python3
# export LITEX_ENV_EFINITY=/home/carlos/Embedded/efinity/2023.2/
#export LITEX_ENV_EFINITY=/Work/CAD/efinity/2024.2/
from migen import *
from board import ECB_T8_T113_V2
from litex.build.generic_platform import *
from litex.build.efinix import EfinixPlatform
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores import dna
from litex.soc.cores.hyperbus import HyperRAM
from liteeth.phy.rmii import LiteEthPHYRMII
from litex.soc.interconnect.csr import *
from litex.soc.cores.dma import WishboneDMAReader
from litex.soc.cores.dma import WishboneDMAWriter
from litex.soc.interconnect import wishbone
from litex.soc.cores.spi import SPIMaster
from litespi.core.master import LiteSPIMaster
from litex.soc.interconnect import stream, wishbone
from migen.genlib.fifo import SyncFIFO


from litex.gen import *

from litex.soc.interconnect.csr import *
from litex.soc.interconnect import stream
from liteeth.common import convert_ip
from liteeth.frontend.stream import LiteEthStream2UDPTX

from litex.soc.cores.bitbang import I2CMaster
from litescope import LiteScopeAnalyzer


#from pwm import PWM 
#from modules import SPIADCWithDMA

#from ver_modules import adc_reader_stream



platform = ECB_T8_T113_V2.Platform()

#!/usr/bin/env python3
# Key fixes applied to original code

class DMAUpload(LiteXModule):
    def __init__(self, bus, udp_port, dst_ip, dst_udp_port):
        # DMA Reader
        # ----------
        self.bus             = bus
        self.dma_reader      = WishboneDMAReader(bus, with_csr=True)
        self.dma_reader_conv = stream.Converter(bus.data_width, 8)

        # UDP Streamer
        # ------------
        udp_streamer   = LiteEthStream2UDPTX(
            ip_address = convert_ip("10.42.0.100"),
            udp_port   = 2000,
            fifo_depth = 1024,
            with_csr   = True
        )


        self.udp_cdc      = stream.ClockDomainCrossing([("data", 8)], "sys", "eth_rx")
        self.udp_streamer = ClockDomainsRenamer("eth_rx")(udp_streamer)

        self.comb += [
            self.dma_reader.source.connect(self.dma_reader_conv.sink),
            self.dma_reader_conv.source.connect(self.udp_cdc.sink),
            self.udp_cdc.source.connect(self.udp_streamer.sink),
            self.udp_streamer.source.connect(udp_port.sink)
        ]

class BaseSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        sys_clk_freq = int(33.333e6)

#        platform.add_source("ver_modules/adc_reader.v")
#        platform.add_source("ver_modules/register_bank.v")
#        platform.add_source("ver_modules/dpram.v")
#        platform.add_source("ver_modules/memory_writer.v")
#        platform.add_source("ver_modules/spi_driver.v")
#        platform.add_source("ver_modules/timmer_sample.v")
        SoCCore.__init__(self, platform,
            cpu_type                 = "femtorv",
            cpu_variant              = "gracilis",  #RV32IMCzCSR
            clk_freq                 = 33.333e6,
            ident                    = "LiteX CPU Test SoC", ident_version=True,
            integrated_rom_size      = 0x9000#,
            #integrated_rom_init      = "./NO_bios_firmware_stream/firmware.bin"

        )

        # Use HyperRAM generic PHY as SRAM
        size = int((8*1024*1024))
        hr_pads = platform.request("hyperram", 0)
        self.hyperram = HyperRAM(hr_pads, latency=7, sys_clk_freq=sys_clk_freq)
        self.bus.add_slave("main_ram",  self.hyperram.bus, SoCRegion(origin=0x40000000, size=size, mode="rw"))

        self.submodules.crg = CRG(platform.request("clk33"), ~platform.request("user_btn_n", 0)) 
        
        self.ethphy  = LiteEthPHYRMII(
          clock_pads = self.platform.request("eth_clocks"),
          pads       = self.platform.request("eth"),
          refclk_cd  = None)

#        self.add_etherbone(
#            phy         = self.ethphy,
#            ip_address  = "10.42.0.220"        
#        )
        self.add_ethernet(
            phy         = self.ethphy,
            data_width  = 32        
        )
        
        bus = wishbone.Interface(
            data_width = self.bus.data_width,
            adr_width  = self.bus.get_address_width(standard="wishbone"),
            addressing = "word",
        )

        # DMA Upload
#        self.submodules.dma_upload = DMAUpload(
#            bus          = bus,
#            udp_port     = self.ethcore_etherbone.udp.crossbar.get_port(2000, dw=8),
#            dst_ip       = "10.42.0.100",
#            dst_udp_port = 2000
#        )
#        self.add_csr("dma_upload")
#        self.bus.add_master("dma_upload", self.dma_upload.dma_reader.bus)

        # PWM module
    #    self.submodules.pwm = PWM(platform.request("user_led",  0))
    #    self.add_csr("pwm")
    #    self.add_csr("spi_dma")

        # I2C module Power supply controller
    #    self.i2c = I2CMaster(pads=platform.request("i2c"))

        #ADC_READER module
    #    SoCCore.add_csr(self,"adc0")
    #    self.submodules.adc1 = adc_reader_stream.StreamADC(platform, 32, 32)

        # DMA Writer 
        wr_bus = wishbone.Interface(data_width=32, adr_width=32, addressing="word")
        self.submodules.dma_writer = dma_writer = WishboneDMAWriter(wr_bus, with_csr=True,  endianness="big")
        self.bus.add_master("dma_writer", master=wr_bus)

        if (0):

            self.comb += [
                self.adc1.source.connect( dma_writer.sink )
            ]

            spi_dma_bus = wishbone.Interface(
                data_width = self.bus.data_width,
                adr_width  = self.bus.get_address_width(standard="wishbone"),
                addressing = "word",
            )

            analyzer_signals = [
                # IBus (could also just added as self.cpu.ibus)
                self.adc0.sclk,
                self.adc0.busy,
                self.adc0.ncs, 
                self.adc0.st_conv,
                self.adc0.data_in,
                self.adc0.reset_ad,
                self.adc0.dout,
            ]
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 512,
                clock_domain = "sys",
                samplerate   = sys_clk_freq,
                csr_csv      = "analyzer.csv")
            self.add_csr("analyzer")

soc = BaseSoC(platform)
# Build --------------------------------------------------------------------------------------------
builder = Builder(soc, output_dir="build/", csr_csv="csr.csv")
builder.build(build_name="top")

#  OTROS EJEMPLOS
#https://github.com/enjoy-digital/litex/wiki/Streams/e08d781947c7a63a6a8c8b2dedcdc9be1b7796a8
#https://github.com/amaranth-lang/amaranth/issues/317#issuecomment-899407394
# When the sink becomes ready (ie the ADC is ready to transmit another byte), the ready signal is asserted, 
# and data can be written by setting up the payload data and asserting the valid signal. 
# When the valid signal is asserted, the data is read by the module.
# see uarty.py as example