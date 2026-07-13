# WS2812 Studio - Architecture

## Modo principal

WS2812 Studio ya no depende de UART para el uso principal. La ruta estable es:

```text
PySide6 UI
-> proyecto .ws2812project
-> generated_animation.h / generated_animation.c
-> firmware RISC-V autonomo
-> ROM embebida en el SoC
-> SRAM framebuffer
-> WishboneDMAReader
-> LiteX Stream
-> WS2812StreamLoader
-> controlador WS2812 Verilog
-> matriz fisica 8x8
```

El boton `COMPILAR Y PROGRAMAR` ejecuta:

```text
validar proyecto
-> generar animacion C
-> compilar firmware
-> regenerar SoC/bitstream
-> validar timing
-> detectar FPGA
-> programar SRAM por FT232RL/JTAG
```

## Modo secundario

El modo `Live UART` queda como opcion secundaria. Requiere un USB-UART conectado
a los pines del SoC (`serial_tx=T6`, `serial_rx=R7`). La ausencia de UART no
bloquea el editor, proyectos, generacion, compilacion ni programacion JTAG.

## Datos generados

Los archivos generados viven en:

```text
Litex/NO_bios_fw_dma/generated_animation.h
Litex/NO_bios_fw_dma/generated_animation.c
```

Formato:

```text
64 palabras por frame
uint32_t por LED
0x00GGRRBB
```

El firmware copia la palabra generada `0x00GGRRBB` directamente al framebuffer
DMA. Esta decision se corrigio con evidencia fisica: convertirla a RGB hacia
que un frame rojo se viera verde. No se modifican FSM, DMA, LiteX Stream,
temporizacion WS2812 ni el pin C4.

## Responsabilidades

| Capa | Responsabilidad |
| --- | --- |
| UI | dibujo, color, timeline, importacion, proyectos, accion Build & Program |
| Codegen | aplica mapeo, brillo y RGB->GRB; emite C determinista |
| Pipeline | compila firmware, genera bitstream, valida timing y programa por JTAG |
| Firmware | reproduce la animacion generada de forma autonoma |
| DMA/Streamer | mueve 64 palabras desde SRAM al periferico |
| RTL WS2812 | genera pulsos temporizados, ya validado |

## Programacion

La programacion es SRAM:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

La animacion se pierde al apagar la FPGA y debe reprogramarse.
