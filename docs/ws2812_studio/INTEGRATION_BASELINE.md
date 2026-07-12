# WS2812 Studio - Integration Baseline

Fecha: 2026-07-12

## Estado Git inicial

Rama funcional de partida: `feat/ws2812-litex-final-project`

Commit funcional usado como base:

```text
f8fbf1d5 Document WS2812 base project
```

Rama nueva de trabajo:

```text
feat/ws2812-studio
```

Remotos verificados:

```text
origin   https://github.com/cicamargoba/digital_UN.git
personal https://github.com/amoralesri/Digital-2.git
```

El push autorizado es solamente a `personal`.

## Hardware confirmado

```text
Placa: Colorlight 5A-75B V8.2
FPGA: Lattice ECP5 LFE5U-25
Matriz: WS2812 8x8, 64 LEDs
DIN: J1 pin fisico 1
Pin FPGA confirmado: C4
Frecuencia SoC: 60 MHz
Salida WS2812: GRB, MSB-first
```

## Target LiteX fisico

Archivo:

```text
Litex/colorlight_5a_75b_ws2812_dma.py
```

Comando base:

```bash
python colorlight_5a_75b_ws2812_dma.py \
  --revision=8.2 \
  --device-override=LFE5U-25F-6BG256C \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

La plataforma confirma:

```text
J1 pin fisico 1 -> j1:0 -> FPGA C4
```

## Firmware C actual

Archivo usado por el target:

```text
Litex/NO_bios_fw_dma/main.c
```

Antes de WS2812 Studio este firmware generaba una secuencia local de prueba. Para Studio se reemplaza por un receptor UART/protocolo que reutiliza las mismas funciones validadas:

```text
ws2812_load_framebuffer()
ws2812_show()
disp0_loader_start_write()
disp0_dma_base_write()
disp0_dma_length_write()
disp0_dma_enable_write()
disp0_init_write()
disp0_done_read()
```

## UART del SoC

El target usa el UART LiteX estandar `serial`.

Helpers reales generados en:

```text
Litex/build/colorlight_5a_75b_ws2812/software/include/generated/csr.h
```

Funciones verificadas:

```c
uart_rxtx_read()
uart_rxtx_write(uint32_t)
uart_txfull_read()
uart_rxempty_read()
uart_ev_pending_write(uint32_t)
```

Baud rate inicial estable:

```text
115200
```

## DMA actual

La ruta validada se conserva:

```text
SRAM framebuffer
-> WishboneDMAReader disp0_dma
-> LiteX Stream
-> WS2812StreamLoader
-> ws2812_periph
-> dout C4
```

Para cada frame se transfieren:

```text
64 palabras de 32 bits = 256 bytes
```

El payload serial de `SET_FRAME` es:

```text
64 pixeles * 3 bytes RGB = 192 bytes
```

El firmware conserva el formato de palabra validado por la ruta DMA existente y el streamer mantiene el orden fisico correcto observado en matriz.

## Puerto serial Linux

La aplicacion detecta puertos con PySerial. El valor esperado para pruebas suele ser:

```text
/dev/ttyUSB0
```

Debe confirmarse en cada equipo con:

```bash
python -m serial.tools.list_ports
```
