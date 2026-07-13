# README WS2812 LiteX

Este documento resume como reproducir el estado actual del periferico WS2812. La documentacion completa esta en `docs/ws2812/`.

## Proyecto base

Desde mi rol de estudiante, este repositorio queda como el proyecto base funcional para controlar una matriz WS2812 con LiteX en la Colorlight 5A-75B V8.2. La secuencia LED ya programada muestra apagado, LEDs individuales, colores solidos, barrido, filas, columnas, ajedrezado y gradiente usando firmware en C, transferencia DMA y un controlador WS2812 en Verilog.

## WS2812 Studio

La rama `feat/ws2812-studio` agrega una aplicacion de escritorio en
`tools/ws2812_studio/` y un firmware autonomo en `Litex/NO_bios_fw_dma/main.c`
para generar animaciones desde el PC, compilar firmware/bitstream y programar
la FPGA por JTAG:

```text
PC -> generated_animation.c -> firmware RISC-V -> bitstream -> FT232RL/JTAG -> matriz fisica
```

Validacion fisica parcial 2026-07-12:

```text
Deteccion JTAG: PASS, IDCODE 0x41111043, Lattice ECP5 LFE5U-25
Programacion SRAM: PASS
Bitstream: Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
UART host observado: /dev/ttyUSB0, FT232RL A50285BI
Baud probado: 115200
Build & Program rojo: PASS hasta programacion SRAM
PING/GET_INFO UART: no requerido en modo principal
```

WS2812 Studio no necesita UART en modo Build & Program. El FT232RL conectado al
header JTAG basta para detectar y programar SRAM. El modo Live UART queda como
opcion secundaria si se conecta un USB-UART a `serial_tx=T6` y `serial_rx=R7`.

## Estado oficial 2026-07-11 V8.2

Placa final:

```text
Colorlight 5A-75B V8.2
FPGA: LFE5U-25F-6BG256C
DIN matriz: J1 pin fisico 1
```

Correspondencia de pin confirmada:

```text
J1 pin fisico 1 -> LiteX j1:0 -> FPGA C4
Constraint: LOCATE COMP "ws28120_dout" SITE "C4";
```

Build final:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_5a_75b_ws2812_dma.py \
  --revision=8.2 \
  --device-override=LFE5U-25F-6BG256C \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

Resultado:

```text
Bitstream: Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
Fmax: 76.58 MHz
Slack setup aprox.: +3.61 ns
Programacion SRAM: PASS con OpenFPGALoader / FT232RL
Validacion visual: PASS; colores, LEDs individuales, filas, columnas, ajedrezado y matriz completa correctos
```

Programacion:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD -m build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

La imagen SRAM cargada actualmente usa un firmware de validacion lenta para distinguir apagado, LED 0, LED 63, colores solidos, barrido, filas, columnas, ajedrezado y frames consecutivos. La validacion fisica final reporta todos esos patrones funcionando correctamente. No se modificaron temporizacion WS2812, FSM, RTL, DMA ni CSR.

## Estado anterior 2026-07-11

La placa objetivo actual es Colorlight 5A-75B. La FPGA fue detectada por JTAG usando FT232RL bit-bang:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

Resultado detectado: `idcode 0x41111043`, Lattice ECP5 `LFE5U-25`. Para la revision asumida `7.0`, la plataforma oficial de `litex_boards` selecciona `LFE5U-25F-6BG256C`, reloj `clk25` en `P6` y `sys_clk_freq=60 MHz`.

Se agrego el target especifico:

```text
Litex/colorlight_5a_75b_ws2812_dma.py
```

El build con RAM integrada, ROM embebida, CSR `disp0`, DMA `disp0_dma`, LiteX stream y controlador WS2812 cierra timing a 60 MHz:

```text
Fmax post-route: 77.97 MHz (PASS at 60.00 MHz)
Slack aproximado del camino critico setup: +3.84 ns
Bitstream: Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

Comando reproducible usado para esta evidencia temporal:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_5a_75b_ws2812_dma.py \
  --revision=7.0 \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

Nota historica: en esta etapa `j1:0` fue usado como pin temporal de build. Esa limitacion quedo reemplazada por la confirmacion V8.2 documentada arriba: `J1 pin fisico 1 -> j1:0 -> FPGA C4`.

## Estado oficial 2026-07-10

El cierre actual adopta 64 LEDs como configuracion verificable del camino WS2812. Se corrigio el RTL para transmitir exactamente direcciones `0..63`, incluir `LED63` y no iniciar `LED64`. Tambien se cerro el timing del build preliminar i5 a 60 MHz despues de mover la lectura del framebuffer a flanco positivo.

Punto critico: la placa objetivo indicada para el proyecto final es Colorlight 5A-75B, pero el arbol local activo integra una plataforma `colorlight_i5` (`LFE5U-25F-6BG381C`, salida `led_matrix.dout` en `G5`). Ese bitstream sirve como evidencia preliminar de SoC/RTL, no como bitstream final confirmado para 5A-75B. No se programo hardware porque no hay cadena JTAG detectada ni revision/pinout 5A-75B confirmados.

## Estado actual

El repositorio contiene un controlador WS2812 jerarquico en `Litex/ws2812/`, integrado a LiteX/Colorlight por dos caminos:

- CSR directo: `Litex/colorlight_i5_no_bios.py` + `Litex/ws2812/ws2812.py`.
- DMA/Stream: `Litex/colorlight_i5_no_bios_dma.py` + `Litex/ws2812/ws2812_streamer.py`.

El flujo principal validado es el DMA/no-BIOS.

## Entorno

Usar el venv local:

```bash
source /home/andresrivera/digital_UN/.venv-litex/bin/activate
```

O pasar Python absoluto:

```bash
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python
```

## Pruebas RTL WS2812

```bash
cd Litex/ws2812
make sim_ws2812_timer_check
make sim_ws2812_full
```

Resultado esperado:

```text
PASS: sel=0 high_cycles=24 total_cycles=75
PASS: sel=1 high_cycles=48 total_cycles=75
PASS: sel=2 high_cycles=0 total_cycles=3002
PASS: 64 LEDs, 1536 bits/frame, GRB MSB-first, LED63, no LED64, second frame
```

## Simulacion SoC DMA reducida

```bash
cd Litex
WAVE=0 VCD=0 FINISH_ON_WS_DONE=1 SIM_N_LEDS=4 SIM_CYCLES=200000 \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make sim_lattice_dma
```

Resultado esperado:

```text
LOADER DONE EDGE: loader_done=1 dma_done=1 writes=64 ...
WS2812 DONE EDGE: ws_done_edges=1 ...
WS2812 completed: observed DMA->WS2812 writes=64 ws_done_edges=1
```

`SIM_N_LEDS=4` solo reduce la duracion de la transmision WS2812 dentro del testbench. El firmware DMA actual configura `WS2812_HW_LEDS=64`, por lo que el DMA carga 256 bytes, equivalentes a 64 palabras de 32 bits.

## Build de bitstream

La variante que genera bitstream en la FPGA `LFE5U-25F` usa RAM integrada para no exceder BRAM:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

Artefacto preliminar i5:

```text
Litex/build/colorlight_i5/gateware/colorlight_i5.bit
```

Resultado actual: el build i5 con RAM integrada genera bitstream, pero la corrida fresca de nextpnr reporta `57.02 MHz (FAIL at 60.00 MHz)`. No usar como bitstream final 5A-75B hasta confirmar revision, paquete, oscilador, JTAG, pin WS2812 y cierre temporal.

## Mapa CSR actual

Mapa generado:

| Bloque | Base |
| --- | ---: |
| `disp0` | `0xf0001000` |
| `disp0_dma` | `0xf0001800` |

Registros principales:

```text
disp0_init          0xf0001000
disp0_rst_cmd       0xf0001004
disp0_done          0xf0001008
disp0_loader_start  0xf000100c
disp0_loader_done   0xf0001010
disp0_loader_busy   0xf0001014
disp0_dma_base      0xf0001800
disp0_dma_length    0xf0001808
disp0_dma_enable    0xf000180c
disp0_dma_done      0xf0001810
disp0_dma_loop      0xf0001814
disp0_dma_offset    0xf0001818
```

## Programacion fisica

No se programo FPGA. La deteccion actual no muestra cable/placa JTAG:

```text
openFPGALoader --scan-usb -> empty
openFPGALoader --detect   -> JTAG init failed
```

Programar solo cuando la placa/cadena esten confirmadas y la matriz tenga alimentacion segura:

```bash
openFPGALoader -m Litex/build/colorlight_i5/gateware/colorlight_i5.bit
```

## Lectura recomendada

1. `docs/ws2812/REQUIREMENTS.md`
2. `docs/ws2812/ARCHITECTURE.md`
3. `docs/ws2812/CSR_MAP.md`
4. `docs/ws2812/MEMORY_AND_BOOT.md`
5. `docs/ws2812/TIMING_REPORT.md`
6. `docs/ws2812/TEST_REPORT.md`
7. `docs/ws2812/DMA_STREAM.md`
8. `docs/ws2812/SYNTHESIS_REPORT.md`
9. `docs/ws2812/PHYSICAL_VALIDATION.md`
10. `docs/ws2812/FINAL_REPORT.md`
