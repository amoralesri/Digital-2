# WS2812 Studio - Physical Test

Estado: BLOCKED hasta programar el firmware UART y observar la matriz fisica.

El proyecto base WS2812 ya estaba validado fisicamente antes de esta rama. Esta
lista corresponde especificamente a la nueva capa WS2812 Studio: PC, UART,
firmware interactivo y envio manual de frames.

Checklist:

1. Compilar firmware Studio. PASS
2. Regenerar bitstream. PASS
3. Programar FPGA.
4. Conectar aplicacion.
5. PING.
6. GET_INFO.
7. CLEAR.
8. Rojo, verde y azul.
9. LED 0.
10. LED 63.
11. Patron manual.
12. Imagen importada.
13. Tres frames en timeline.
14. Live Sync.
15. Desconexion y reconexion.

## Datos de build

```text
Placa: Colorlight 5A-75B V8.2
FPGA: LFE5U-25F-6BG256C
DIN: J1 pin fisico 1
Pin FPGA real: C4
Frecuencia: 60 MHz
Fmax: 72.39 MHz
Slack minimo observado: >= 2.543 ns
Bitstream: Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

## Programacion sugerida

Detectar:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

Resultado en esta sesion:

```text
Codigo de retorno: 1
Salida:
unable to open ftdi device: -3 (device not found)
JTAG init failed with: unable to open ftdi device
empty
```

Por este motivo no se programo la FPGA desde esta sesion.

Programar SRAM:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD \
  Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

No marcar PASS sin observacion fisica.
