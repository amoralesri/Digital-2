#   run make TOP=SOC or make TOP=SOC_flash
EFINITY_HOME  = /home/carlos/Embedded/efinity/2023.2/
EFXPT_HOME    = $(EFINITY_HOME)/pt

TARGET=colorlight_i5
TOP=colorlight_i5

EFINIX_SIM_CELLS   = sim_models_efx/efx_ff.v  sim_models_efx/efx_dpram_5k.v sim_models_efx/efx_ram_5k.v sim_models_efx/efx_lut4.v sim_models_efx/efx_add.v sim_models_efx/efx_gbufce.v 
LATTICE_SIM_CELLS  = ./lattice_sim/cells_sim_ecp5.v  lattice_sim/sim_pll.v ./lattice_sim/cells_ff.vh lattice_sim/mult18x18d.v
SERIAL = /dev/ttyUSB1
PYTHON ?= python3
WAVE ?= 1
VCD ?= 1
SIM_CYCLES ?= 50000
FINISH_ON_WS_DONE ?= 0
SIM_N_LEDS ?= 64
WS_DONE_EDGES ?= 1

COMM_OBJS=  mult/mult_32.v
COMM_OBJS+= mult/control_mult.v
COMM_OBJS+= mult/acc.v
COMM_OBJS+= mult/comp.v
COMM_OBJS+= mult/lsr_mult.v
COMM_OBJS+= mult/rsr.v

COMM_OBJS+= ws2812/ctrl_wsled.v
COMM_OBJS+= ws2812/ws2812.v
COMM_OBJS+= ws2812/comp_ws_arr.v
COMM_OBJS+= ws2812/count_wsled.v
COMM_OBJS+= ws2812/ws2812_led_array.v
COMM_OBJS+= ws2812/ctrl_ws.v
COMM_OBJS+= ws2812/comp_ws.v
COMM_OBJS+= ws2812/count_ws.v
COMM_OBJS+= ws2812/lsr_wsled.v
COMM_OBJS+= ws2812/ws2812_led.v
COMM_OBJS+= ws2812/ws2812_periph.v
COMM_OBJS+= ws2812/count_addr.v
COMM_OBJS+= ws2812/ctrl_ws_arr.v
COMM_OBJS+= ws2812/led_mem_dual.v
COMM_OBJS+= ws2812/mux_ws.v
    
                        


OBJS = build/colorlight_i5/gateware/colorlight_i5.v
OBJS+= VexRiscv.v

OBJS += $(COMM_OBJS)

BUILD_DIR = build
SOC_SCRIPT="colorlight_i5_no_bios.py"
SOC_SCRIPT_DMA="colorlight_i5_no_bios_dma"
SOC_DMA_TB=colorlight_i5_dma_TB
FW_NB_DIR = NO_bios_fw
FW_NB_DMA_DIR = NO_bios_fw_dma

BUILD_DIR="build/colorlight_i5"
ROM_SIZE=65536




all: sim


fw_no_bios:
	rm -rf *vpp *.vcd build $(FW_NB_DIR)/*bin
	dd if=/dev/zero of=$(FW_NB_DIR)/firmware.bin bs=1 count=$(ROM_SIZE) status=none

	@echo "=== [2/6] Generando regions.ld y headers CSR ==="
	$(PYTHON) $(SOC_SCRIPT) --build --no-compile-gateware --no-compile-software 2>&1 | \
	    grep -E "INFO|ERROR|WARNING|rom|sram" || true
	@grep "rom" build/colorlight_i5/software/include/generated/regions.ld

	@echo "=== Compilando librerías software (picolibc…) ==="
	$(PYTHON) $(SOC_SCRIPT) --build --no-compile-gateware 2>&1 | tail -5

	make -C ${FW_NB_DIR}/ 2>&1
	FW_SIZE=$(ls -lah ${FW_NB_DIR}/firmware.bin | awk '{print $5}')
	$(PYTHON) colorlight_i5_no_bios.py --build  --board=i9 --revision=7.2 --load


sim_efinix:
	rm -f *vpp *.vcd build
	yosys -v3 -l synth.log -p ' synth_efinix -top $(TOP) -json $(TOP).json; write_verilog -attr2comment $(TOP)_synth.v' ${OBJS}
	iverilog -o $@_PS.vpp -s $(TARGET)_TB $(TARGET)_TB.v $(TOP)_synth.v $(EFINIX_SIM_CELLS) 
	vvp $@_PS.vpp
	gtkwave $(TARGET)_TB.vcd
	
sim_lattice:
	rm -rf build *vpp *vcd $(FW_NB_DIR)/*bin
	dd if=/dev/zero of=$(FW_NB_DIR)/firmware.bin bs=1 count=$(ROM_SIZE) status=none
	$(PYTHON) $(SOC_SCRIPT) --build --no-compile-gateware --no-compile-software
	$(PYTHON) $(SOC_SCRIPT) --build --no-compile-gateware 2>&1 | tail -5
	$(MAKE) -C $(FW_NB_DIR)/
	SIMULATION=1 $(PYTHON) $(SOC_SCRIPT) --build --no-compile-gateware --no-compile-software 2>&1 | \
	    grep -E "INFO|ERROR|WARNING" || true
	cp build/colorlight_i5/gateware/colorlight_i5_rom.init .
	cp build/colorlight_i5/gateware/colorlight_i5_sram.init .
	iverilog -I ./lattice_sim \
	    -o $@_PS.vpp \
	    -s $(TARGET)_TB \
	    -P $(TARGET)_TB.enable_vcd=$(VCD) \
	    -P $(TARGET)_TB.sim_cycles=$(SIM_CYCLES) \
	    -P $(TARGET)_TB.finish_on_ws_done=$(FINISH_ON_WS_DONE) \
	    -P $(TARGET)_TB.sim_n_leds=$(SIM_N_LEDS) \
	    -P $(TARGET)_TB.finish_after_ws_done_edges=$(WS_DONE_EDGES) \
	    $(TARGET)_TB.v \
	    $(OBJS) \
	    $(LATTICE_SIM_CELLS)
	vvp $@_PS.vpp
	@if [ "$(WAVE)" = "1" ]; then gtkwave $(TARGET)_TB.vcd; fi

sim_lattice_dma:
	rm -rf build *vpp *vcd $(FW_NB_DMA_DIR)/*bin
	dd if=/dev/zero of=$(FW_NB_DMA_DIR)/firmware.bin bs=1 count=$(ROM_SIZE) status=none
	SIMULATION=1 $(PYTHON) $(SOC_SCRIPT_DMA).py --build --no-compile-gateware --no-compile-software 2>&1 | \
	    grep -E "INFO|ERROR|WARNING|rom|sram|disp0" || true
	SIMULATION=1 $(PYTHON) $(SOC_SCRIPT_DMA).py --build --no-compile-gateware --no-compile-software
	mkdir -p build/colorlight_i5/software/libc
	cp $$(grep '^LIBC_DIRECTORY=' build/colorlight_i5/software/include/generated/variables.mak | cut -d= -f2)/picolibc-minimal.h build/colorlight_i5/software/libc/picolibc.h
	printf '#define FORMAT_DEFAULT_INTEGER\n#define __IO_DEFAULT '\''i'\''\n' >> build/colorlight_i5/software/libc/picolibc.h
	$(MAKE) -C $(FW_NB_DMA_DIR)/
	SIMULATION=1 $(PYTHON) $(SOC_SCRIPT_DMA).py --build --no-compile-gateware --no-compile-software 2>&1 | \
	    grep -E "INFO|ERROR|WARNING" || true
	cp build/colorlight_i5/gateware/colorlight_i5_rom.init .
	cp build/colorlight_i5/gateware/colorlight_i5_sram.init .
	iverilog -I ./lattice_sim \
	    -o $@_PS.vpp \
	    -s $(SOC_DMA_TB) \
	    -P colorlight_i5_dma_TB.enable_vcd=$(VCD) \
	    -P colorlight_i5_dma_TB.sim_cycles=$(SIM_CYCLES) \
	    -P colorlight_i5_dma_TB.finish_on_ws_done=$(FINISH_ON_WS_DONE) \
	    -P colorlight_i5_dma_TB.sim_n_leds=$(SIM_N_LEDS) \
	    -P colorlight_i5_dma_TB.finish_after_ws_done_edges=$(WS_DONE_EDGES) \
	    $(SOC_DMA_TB).v \
	    $(OBJS) \
	    $(LATTICE_SIM_CELLS)
	vvp $@_PS.vpp
	@if [ "$(WAVE)" = "1" ]; then gtkwave colorlight_i5_dma_TB.vcd colorlight_i5_no_bios_dma_sim.gtkw; fi


svg:
	yosys -p "prep -top ${TARGET}; write_json ${TARGET}.json" -DPASSTHROUGH_PLL -DBOARD_FREQ=27 -DCPU_FREQ=27  ${OBJS}
	netlistsvg ${TARGET}.json -o ${TARGET}.svg  #--skin default.svg
	yosys -p "prep -top ${TARGET} -flatten; write_json ${TARGET}_flat.json" ${OBJS}
	netlistsvg ${TARGET}_flat.json -o ${TARGET}_flat.svg  #--skin default.svg




##########################
#    EFINIX ECB_T20_T113
##########################
EFINITY_HOME=/home/carlos/Embedded/efinity/2023.2/
EFXPT_HOME=$(EFINITY_HOME)/pt
create_files:
	export EFINITY_HOME=/home/carlos/Embedded/efinity/2023.2/
	export EFXPT_HOME=$(EFINITY_HOME)/pt
	$(EFINITY_HOME)/bin/python3  femtorv32.py
synth: create_files
	$(EFINITY_HOME)/bin/efx_map --project "$(TOP)" --root "$(TOP)" --write-efx-verilog "outflow/$(TOP).map.v" --write-premap-module "outflow/$(TOP).elab.vdb" --binary-db "outflow/$(TOP).vdb" --device "T20Q144" --family "Trion" --veri_option "verilog_mode=verilog_2k,vhdl_mode=vhdl_2008" --work-dir "work_syn" --output-dir "outflow" --project-xml "$(TOP).xml" --I "."
place_and_route: synth
	$(EFINITY_HOME)/bin/python3  "/home/carlos/Embedded/efinity/2023.2/scripts/efx_run_pt.py"  "$(TOP)"  "Trion"  "T20Q144"
	$(EFINITY_HOME)/bin/efx_pnr --circuit "$(TOP)" --family "Trion" --device "T20Q144" --operating_conditions "C3" --pack --place --vdb_file "outflow/$(TOP).vdb" --use_vdb_file "on" --place_file "outflow/$(TOP).place" --route_file "outflow/$(TOP).route" --sdc_file "$(TOP).sdc" --sync_file "outflow/$(TOP).interface.csv" --seed "1" --placer_effort_level "2" --max_threads "-1" --print_critical_path "10" --work_dir "work_pnr" --output_dir "outflow" --timing_analysis "on" --load_delay_matrix
	$(EFINITY_HOME)/bin/efx_pnr --circuit "$(TOP)" --family "Trion" --device "T20Q144" --operating_conditions "C3" --route --vdb_file "outflow/$(TOP).vdb" --use_vdb_file "on" --place_file "outflow/$(TOP).place" --route_file "outflow/$(TOP).route" --sdc_file "$(TOP).sdc" --sync_file "outflow/$(TOP).interface.csv" --seed "1" --placer_effort_level "2" --max_threads "-1" --print_critical_path "10" --work_dir "work_pnr" --output_dir "outflow" --timing_analysis "on" --load_delay_matrix
bitstream: place_and_route
	$(EFINITY_HOME)/bin/efx_pgm --source "work_pnr/$(TOP).lbf" --dest "outflow/$(TOP).hex" --device "T20Q144" --family "Trion" --periph "outflow/$(TOP).lpf" --interface_designer_settings "outflow/$(TOP)_or.ini" --enable_external_master_clock "off" --oscillator_clock_divider "DIV8" --active_capture_clk_edge "posedge" --spi_low_power_mode "on" --io_weak_pullup "on" --enable_roms "smart" --mode "active" --width "1" --release_tri_then_reset "on"
configure_efinix: outflow/$(TOP).bit
	openFPGALoader -b trion_t120_bga576  outflow/$(TOP).bit
clean_efinix:
	rm -rf work_pnr work_pt work_syn outflow $(TOP).peri.xml

######################
#    SPI  FLASH      #
######################

##########################
#    EFINIX ECB_T20_T113
##########################

EFINITY_HOME=/home/carlos/Embedded/efinity/2023.2/
EFXPT_HOME=$(EFINITY_HOME)/pt

svg_flash: $(FLASH_OBJS)
	yosys -p "prep -top ${TARGET}; write_json ${TARGET}.json" -DPASSTHROUGH_PLL -DBOARD_FREQ=27 -DCPU_FREQ=27  ${FLASH_OBJS}
	netlistsvg ${TARGET}.json -o ${TARGET}_flash.svg  #--skin default.svg
	yosys -p "prep -top ${TARGET} -flatten; write_json ${TARGET}_flat.json" ${FLASH_OBJS}
	netlistsvg ${TARGET}_flat.json -o ${TARGET}_flat_flash.svg  #--skin default.svg

litex_term:
	@ls ${SERIAL} || (echo "\n\nNo se encuentra ${SERIAL} conectado, verifique conexión o cambie el valor de SERIAL=${SERIAL} por un puerto serial existente\n\n"; exit 123;)
	litex_term ${SERIAL} --kernel firmware/firmware.bin


clean_efinix_flash:
	rm -rf work_pnr work_pt work_syn outflow $(TOP).peri.xml

clean: clean_efinix_flash  clean_efinix
	rm -rf impl obj_dir *svg a.out *.vcd *.json *.bit build *synth.v *vpp *vcd
