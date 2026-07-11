# Reporte final WS2812 LiteX

Fecha local: 2026-07-10
Repositorio: `/home/andresrivera/digital_UN`
Rama: `feat/ws2812-litex-final-project`

## Actualizacion 2026-07-11 - Colorlight 5A-75B

Se avanzo desde el estado bloqueado anterior hasta un build especifico de Colorlight 5A-75B con timing cerrado. La validacion fisica todavia no se marca como terminada porque falta confirmar dos datos externos al repositorio: revision impresa de la PCB y pin fisico real conectado a DIN de la matriz WS2812.

| Punto | Resultado |
| --- | --- |
| FPGA detectada | PASS, `openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect` |
| IDCODE | `0x41111043` |
| Familia/modelo JTAG | Lattice ECP5, `LFE5U-25` |
| Plataforma usada | `litex_boards.platforms.colorlight_5a_75b`, revision asumida `7.0` |
| FPGA/package de plataforma | `LFE5U-25F-6BG256C` |
| Frecuencia final | 60 MHz |
| Timing post-route | `77.97 MHz (PASS at 60.00 MHz)` |
| Slack setup aprox. | `+3.84 ns` sobre periodo de 16.67 ns |
| Memoria final | ROM integrada 64 KiB, SRAM 8 KiB, main RAM 8 KiB |
| CSR principales | `disp0=0xf0000800`, `disp0_dma=0xf0001000` |
| Bitstream generado | `Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit` |
| Pin WS2812 | `j1:0` usado solo como pin temporal de build; pin fisico final pendiente |
| Programacion FPGA | BLOCKED, no ejecutada con bitstream final por falta de pin/revision fisica confirmados |
| Validacion matriz | BLOCKED, no ejecutada |

Comandos principales ejecutados:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

```bash
cd Litex
BUILD_DIR=../build/colorlight_5a_75b_ws2812/ \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make -C NO_bios_fw_dma
```

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_5a_75b_ws2812_dma.py \
  --revision=7.0 \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

Archivos nuevos relevantes:

```text
Litex/colorlight_5a_75b_ws2812_dma.py
docs/ws2812/log_hw_detect_5a75b_ft232rl_20260711.txt
docs/ws2812/log_build_5a75b_ws2812_60mhz_seed1_j1_0_rerun.txt
docs/ws2812/log_fw_5a75b_ws2812_dma_j1_0_final.txt
```

Estado global: `BLOCKED` para cierre definitivo fisico. La parte de deteccion, firmware, build, recursos y timing de la variante 5A-75B queda verificada; la programacion y patrones fisicos siguen pendientes.

## Actualizacion de cierre oficial

Se completo una segunda ronda de cierre sobre 64 LEDs. El periferico ahora transmite exactamente 64 LEDs por frame (`0..63`), evita el inicio espurio de `LED64`, conserva orden GRB MSB-first y soporta frames consecutivos. El firmware DMA carga 64 palabras de 32 bits por frame, equivalentes a 256 bytes.

La sintesis preliminar para la plataforma local `colorlight_i5` con RAM integrada genera bitstream, pero la corrida fresca no cierra timing a 60 MHz: nextpnr reporta `57.02 MHz (FAIL at 60.00 MHz)`. Este resultado no valida aun la placa final Colorlight 5A-75B, porque falta confirmar revision fisica, FPGA/paquete, oscilador, cadena JTAG, pin real de salida WS2812 y cierre temporal. Por seguridad no se programo hardware.

## Resultado actualizado

| Area | Estado | Evidencia |
| --- | --- | --- |
| RTL WS2812 64 LEDs | PASS | `make sim_ws2812_full` |
| Timer WS2812 60 MHz | PASS | `make sim_ws2812_smoke` |
| CSR directo 64 LEDs | PASS | `log_sim_lattice_csr_64led_posedge_mem_retry.txt` |
| DMA 64 palabras/frame | PASS | `log_sim_lattice_dma_64led_two_frames_posedge_mem.txt` |
| Build i5 RAM integrada | PASS build / FAIL timing | `log_build_i5_dma_integrated_ram_64led_60mhz_posedge_mem_final.txt` |
| Colorlight 5A-75B final | BLOCKED | revision/pinout/JTAG no confirmados |
| Programacion FPGA | NO EJECUTADA | `openFPGALoader --detect` sin cable/placa |

Los apartados historicos siguientes quedan como trazabilidad de la ronda anterior; los valores de 256 LEDs y timing fallido fueron reemplazados por el cierre de 64 LEDs descrito arriba.

## Objetivo

Continuar el proyecto WS2812 desde el estado actual, sin descartar cambios locales, y cerrar la mayor cantidad posible de evidencia: dependencias, simulacion, CSR, firmware, sintesis, bitstream y validacion fisica segura.

## Cambios tecnicos realizados

- Se creo `.venv-litex` con LiteX/Migen/litedram/liteeth/litespi y pythondata necesarios.
- Se corrigieron APIs LiteX obsoletas: `SoCCore.add_csr(...)` -> `self.csr.add(...)`.
- Se ajustaron Makefiles no-BIOS para compilar firmware sin depender de `/srv/tftp`.
- Se corrigieron linkers no-BIOS para `.srodata`, `.got`, `.toc`, arrays de init/fini y simbolos usados por `startup.c`.
- Se renombro `busy_wait` en firmware DMA a `ws2812_delay` para evitar conflicto con LiteX.
- Se actualizo el timing WS2812 a 60 MHz: `T0H=24`, `T1H=48`, `PER=73`, `RES=3000`.
- Se ensancharon contador, mux y comparador WS2812 a 16 bits.
- Se separo inicializacion de framebuffer para simulacion/sintesis en `led_mem_dual.v`.
- Se instrumento `colorlight_i5_dma_TB.v` para distinguir `loader_done` de `ws2812_periph.done`.
- Se agregaron parametros de simulacion: `WAVE`, `VCD`, `SIM_CYCLES`, `FINISH_ON_WS_DONE`, `SIM_N_LEDS`.
- Se corrigio el UART auxiliar DMA de pines invalidos `Y4/Y6` a pines validos `C17/B18`.

## Resultados

| Area | Estado | Evidencia |
| --- | --- | --- |
| Dependencias LiteX | PASS | imports en `.venv-litex` |
| Timer WS2812 60 MHz | PASS | `make sim_ws2812_timer_check` |
| Firmware no-BIOS DMA | PASS | `firmware.elf/bin/lst`, entry `0x0` |
| CSR `disp0`/`disp0_dma` | PASS | `build/colorlight_i5/csr.csv`, `csr.h` |
| Simulacion SoC DMA reducida | PASS | DMA 256 writes + `WS2812 DONE EDGE` |
| Simulacion SoC 256 completa | PASS parcial | loader/DMA completo; transmision 256 lenta en Icarus |
| Build con SDRAM | FAIL recursos | `DP16KD: 60/56` |
| Build con RAM integrada | PASS | `colorlight_i5.bit` generado |
| Timing FPGA 60 MHz | FAIL/WARNING | max 57.14 MHz vs 60 MHz |
| Validacion fisica | BLOCKED | FT232R visible, JTAG no detectado |

## Comandos clave

```bash
cd Litex/ws2812
make sim_ws2812_timer_check
```

```bash
cd Litex
WAVE=0 VCD=0 FINISH_ON_WS_DONE=1 SIM_N_LEDS=4 SIM_CYCLES=200000 \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make sim_lattice_dma
```

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

## Artefactos importantes

```text
Litex/NO_bios_fw_dma/firmware.elf
Litex/NO_bios_fw_dma/firmware.bin
Litex/build/colorlight_i5/software/include/generated/csr.h
Litex/build/colorlight_i5/csr.csv
Litex/build/colorlight_i5/gateware/colorlight_i5.bit
docs/ws2812/log_sim_lattice_dma_ws_done_reduced.txt
docs/ws2812/log_build_colorlight_i5_no_bios_dma_integrated_ram.txt
```

## Limitaciones

- El bitstream existe, pero no cierra timing a 60 MHz.
- No se programo la FPGA por falta de deteccion inequívoca de JTAG/target.
- El build con SDRAM externa no cabe en BRAM del `LFE5U-25F` con este SoC.
- La simulacion completa de 256 LEDs a nivel SoC es muy lenta en Icarus; se valido un caso reducido de transmision con `SIM_N_LEDS=4`.

## Siguiente trabajo recomendado

1. Bajar `sys_clk_freq` o optimizar camino critico para cerrar timing.
2. Definir oficialmente si el proyecto final usa RAM integrada o SDRAM.
3. Confirmar hardware/programador antes de cargar bitstream.
4. Hacer prueba fisica con brillo bajo, fuente externa y GND comun.
5. Agregar autochecks para frames de mas LEDs sin depender de VCD.
