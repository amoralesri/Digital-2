# Matriz de pruebas WS2812

Fecha local: 2026-07-10

Solo se marca PASS cuando el comando fue ejecutado realmente.

## Actualizacion 2026-07-11 - Colorlight 5A-75B

| ID | Nivel | Comando | Resultado real | Estado |
| --- | --- | --- | --- | --- |
| T16 | Deteccion FT232RL/JTAG | `openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect` | `idcode 0x41111043`, Lattice ECP5 `LFE5U-25` | PASS |
| T17 | Firmware DMA para headers 5A-75B | `BUILD_DIR=../build/colorlight_5a_75b_ws2812/ PYTHON=... make -C NO_bios_fw_dma` | `firmware.bin` generado, ROM 1.34 KiB, SRAM 0.25 KiB | PASS |
| T18 | Build 5A-75B 60 MHz | `python colorlight_5a_75b_ws2812_dma.py --revision=7.0 --ws2812-pin j1:0 --build --no-compile-software --nextpnr-seed 1` | `77.97 MHz (PASS at 60.00 MHz)`, bitstream generado | PASS |
| T19 | Programacion FPGA | No ejecutado | Pendiente pin fisico DIN y revision exacta PCB | BLOCKED |
| T20 | Patrones fisicos matriz | No ejecutado | Pendiente programacion segura | BLOCKED |

Logs:

```text
docs/ws2812/log_hw_detect_5a75b_ft232rl_20260711.txt
docs/ws2812/log_fw_5a75b_ws2812_dma_j1_0_final.txt
docs/ws2812/log_build_5a75b_ws2812_60mhz_seed1_j1_0_rerun.txt
```

## Actualizacion de cierre 64 LEDs

| ID | Nivel | Comando | Resultado real | Estado |
| --- | --- | --- | --- | --- |
| T10 | RTL completo 64 LEDs | `cd Litex/ws2812 && make sim_ws2812_full` | 1536 bits/frame, GRB MSB-first, `LED63` incluido, `LED64` no iniciado, segundo frame correcto | PASS |
| T11 | RTL smoke timer | `cd Litex/ws2812 && make sim_ws2812_smoke` | `T0H=24`, `T1H=48`, periodo 75 ciclos, reset 3002 ciclos | PASS |
| T12 | SoC CSR directo 64 LEDs | `make sim_lattice` con `FINISH_ON_WS_DONE=1 SIM_N_LEDS=64` | 64 escrituras CSR, `max_addr=63`, `MEM[63]=000049`, `ws_done_edges=1` | PASS |
| T13 | SoC DMA 64 palabras, 2 frames | `make sim_lattice_dma` con `WS_DONE_EDGES=2 SIM_N_LEDS=4` | `writes=128`, `loader_done_edges=2`, `ws_done_edges=2`, `MEM[63]=100000` | PASS |
| T14 | Build i5 60 MHz posedge RAM | `python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000` | bitstream generado, `57.02 MHz (FAIL at 60.00 MHz)` | PASS build / FAIL timing |
| T15 | JTAG/hardware | `lsusb`, `openFPGALoader --scan-usb`, `openFPGALoader --detect` | no aparece FTDI/JTAG; `--detect` falla | BLOCKED |

Logs nuevos:

```text
docs/ws2812/log_sim_lattice_csr_64led_posedge_mem_retry.txt
docs/ws2812/log_sim_lattice_dma_64led_two_frames_posedge_mem.txt
docs/ws2812/log_build_i5_dma_integrated_ram_64led_60mhz_posedge_mem_final.txt
```

La matriz historica siguiente conserva los resultados previos de 256 LEDs como trazabilidad; el cierre actual del proyecto usa 64 LEDs verificados.

| ID | Nivel | Comando | Resultado real | Estado |
| --- | --- | --- | --- | --- |
| T01 | Timer RTL | `cd Litex/ws2812 && make sim_ws2812_timer_check` | `24/48/75/3002` ciclos medidos | PASS |
| T02 | SoC DMA reducido | `make sim_lattice_dma` con `SIM_N_LEDS=4 FINISH_ON_WS_DONE=1` | DMA escribio 256 palabras y `ws2812_periph.done` subio | PASS |
| T03 | SoC DMA 256 completo | VVP directo sobre `sim_lattice_dma_PS.vpp` | `loader_done=1`, `writes=256`; transmision completa muy lenta en Icarus | PASS parcial |
| T04 | Firmware no-BIOS DMA | `make -C NO_bios_fw_dma` via target SoC | `firmware.elf/bin/lst` generados | PASS |
| T05 | Firmware no-BIOS base | `make -C NO_bios_fw` via target SoC | `firmware.elf/bin/lst` generados | PASS |
| T06 | CSR generado | build LiteX DMA | `disp0` y `disp0_dma` en `csr.h/csr.csv` | PASS |
| T07 | Build SoC con SDRAM | `python colorlight_i5_no_bios_dma.py --build --no-compile-software` | Falla por `DP16KD: 60/56` | FAIL recursos |
| T08 | Build SoC RAM integrada | `python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000` | Bitstream generado | PASS con warning timing |
| T09 | Deteccion fisica | `openFPGALoader --scan-usb`, `--detect` | FT232R visible, JTAG no detectado | BLOCKED |

## Salidas clave

### Timer

```text
PASS: sel=0 high_cycles=24 total_cycles=75
PASS: sel=1 high_cycles=48 total_cycles=75
PASS: sel=2 high_cycles=0 total_cycles=3002
PASS: ws2812 timer protocol check completed
```

### Simulacion SoC DMA reducida

Comando:

```bash
cd Litex
WAVE=0 VCD=0 FINISH_ON_WS_DONE=1 SIM_N_LEDS=4 SIM_CYCLES=200000 \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make sim_lattice_dma
```

Salida relevante:

```text
LOADER DONE EDGE: loader_done=1 dma_done=1 writes=256 ...
WS2812 DONE EDGE: ws_done_edges=1 loader_done=1 dma_done=0 writes=256 ws_addr=4 ...
WS2812 completed: observed DMA->WS2812 writes=256 ws_done_edges=1
```

`SIM_N_LEDS=4` es solo un parametro del testbench para que el VVP termine en tiempo razonable. El firmware y el loader siguen cargando 256 palabras.

### Simulacion 256 LEDs

La corrida completa de 256 LEDs se considera demasiado lenta en Icarus a nivel SoC/VexRiscv. Una ejecucion directa de 25 s alcanzo:

```text
LOADER DONE EDGE: loader_done=1 dma_done=1 writes=256 ...
```

No se marca PASS completo de transmision de 256 LEDs por simulacion.

## Logs

Logs guardados:

```text
docs/ws2812/log_sim_lattice_dma_ws_done_reduced.txt
docs/ws2812/log_build_colorlight_i5_no_bios_dma.txt
docs/ws2812/log_build_colorlight_i5_no_bios_dma_integrated_ram.txt
```
