# Camino DMA/Stream WS2812

Fecha local: 2026-07-10

## Resumen

El camino DMA validado usa `Litex/colorlight_i5_no_bios_dma.py`, `Litex/NO_bios_fw_dma/main.c` y `Litex/ws2812/ws2812_streamer.py`.

La configuracion verificable actual es de 64 LEDs. El firmware define:

```c
#define WS2812_HW_LEDS 64u
```

Por eso `disp0_dma_length_write(WS2812_HW_LEDS * 4u)` programa una transferencia de 256 bytes. En LiteX `WishboneDMAReader` se observan 64 palabras/beats de 32 bits por frame, no 256 palabras.

## Flujo de datos

```text
SRAM software buffer
  -> WishboneDMAReader
  -> LiteX stream 32-bit
  -> WS2812StreamLoader
  -> w_address/w_data/we_a
  -> led_mem_dual framebuffer
  -> ws2812_periph serial dout
```

`WS2812StreamLoader` recibe una palabra de 32 bits, conserva 24 bits RGB utiles y escribe una posicion del framebuffer. El periferico serializa en orden GRB, MSB-first, segun la convencion WS2812.

## Evidencia ejecutada

Simulacion DMA reducida a 4 LEDs transmitidos por el testbench, con carga real de 64 palabras:

```bash
cd Litex
WAVE=0 VCD=0 FINISH_ON_WS_DONE=1 SIM_N_LEDS=4 SIM_CYCLES=200000 \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make sim_lattice_dma
```

Resultado relevante:

```text
LOADER DONE EDGE: loader_done=1 dma_done=1 writes=64 dma_len_words=64
WS2812 DONE EDGE: ws_done_edges=1 ... writes=64 ws_addr=3
```

Simulacion DMA de dos frames:

```bash
cd Litex
WAVE=0 VCD=0 FINISH_ON_WS_DONE=1 WS_DONE_EDGES=2 SIM_N_LEDS=4 SIM_CYCLES=800000 \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make sim_lattice_dma
```

Resultado relevante:

```text
LOADER DONE EDGE: ... writes=128 dma_len_words=64
WS2812 DONE EDGE: ws_done_edges=2 ... mem0=100000 mem63=100000
WS2812 completed: observed DMA->WS2812 writes=128 loader_done_edges=2 ws_done_edges=2
```

Logs:

```text
docs/ws2812/log_sim_lattice_dma_64led_reduced.txt
docs/ws2812/log_sim_lattice_dma_64led_two_frames.txt
docs/ws2812/log_sim_lattice_dma_64led_two_frames_posedge_mem.txt
```

## Nota de concurrencia

Los targets `sim_lattice` y `sim_lattice_dma` no deben correrse en paralelo porque ambos eliminan y regeneran `Litex/build`. Una corrida paralela puede mezclar headers CSR de variantes distintas y provocar errores de compilacion de firmware.
