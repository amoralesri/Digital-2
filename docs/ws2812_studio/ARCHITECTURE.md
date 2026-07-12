# WS2812 Studio - Architecture

```text
PySide6 UI
-> DeviceController
-> SerialTransport / SimulatedTransport
-> protocolo binario CRC16
-> UART LiteX
-> firmware RISC-V
-> SRAM framebuffer
-> WishboneDMAReader
-> LiteX Stream
-> WS2812StreamLoader
-> controlador WS2812 Verilog
-> matriz fisica 8x8
```

## Responsabilidades

| Capa | Responsabilidad |
| --- | --- |
| UI | dibujo, color, timeline, importacion, Live Sync |
| DeviceController | empaqueta comandos, aplica brillo y mapeo |
| Protocol | SOF/version/command/sequence/length/CRC |
| Firmware | parser UART, validacion, ACK/NACK, control DMA |
| DMA/Streamer | mueve 64 palabras desde SRAM al periférico |
| RTL WS2812 | genera pulsos temporizados, ya validado |

No se redisenaron FSM, temporizador, DMA Reader, streamer ni pinout fisico.
