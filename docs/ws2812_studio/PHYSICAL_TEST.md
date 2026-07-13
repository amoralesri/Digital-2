# WS2812 Studio - Physical Test

Estado: BLOCKED en confirmacion visual de la matriz.

El proyecto base WS2812 ya estaba validado fisicamente antes de esta rama. Esta
lista corresponde especificamente a la nueva capa WS2812 Studio en modo
Build & Program: PC, generacion C, firmware autonomo, bitstream y JTAG.

Checklist:

1. Compilar firmware Studio. PASS
2. Regenerar bitstream. PASS
3. Programar FPGA. PASS
4. Generar firmware. PASS
5. Compilar firmware. PASS
6. Regenerar bitstream. PASS
7. Detectar FPGA desde pipeline. PASS
8. Rojo. BLOCKED, programado pero pendiente de confirmacion visual
9. Verde. BLOCKED
10. Azul. BLOCKED
11. LED 0. BLOCKED
12. LED 63. BLOCKED
13. Patron manual. BLOCKED
14. Imagen importada. BLOCKED
15. Tres frames en timeline. BLOCKED
16. Live Sync UART. N/A para modo principal
17. Desconexion y reconexion UART. N/A para modo principal

## Datos de build

```text
Placa: Colorlight 5A-75B V8.2
FPGA: LFE5U-25F-6BG256C
DIN: J1 pin fisico 1
Pin FPGA real: C4
Frecuencia: 60 MHz
Fmax: 75.00 MHz
Slack minimo observado: >= 2.195 ns
Bitstream: Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
UART LiteX: serial_tx=T6, serial_rx=R7
UART host observado: /dev/ttyUSB0, FTDI A50285BI
Baud rate probado: 115200
Modo principal: Build & Program por JTAG, sin UART
```

## Deteccion y programacion

Detectar:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

Resultado:

```text
empty
Jtag probe limited to 3MHz
Jtag frequency : requested 6000000Hz -> real 3000000Hz
ret 0
index 0:
        idcode 0x41111043
        manufacturer lattice
        family ECP5
        model  LFE5U-25
        irlength 8
```

Codigo de retorno: 0.

Programar SRAM:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

Resultado:

```text
Open file: DONE
Parse file: DONE
Enable configuration: DONE
SRAM erase: DONE
Loading: 100.00%
Done
Disable configuration: DONE
```

Codigo de retorno: 0.

Deteccion posterior a programacion: PASS con el mismo IDCODE `0x41111043`.

## UART

Dispositivos observados:

```text
/dev/ttyUSB0 -> FT232RL, serial A50285BI
/dev/ttyACM* -> no existe
dmesg -> no accesible sin permisos
```

Permisos:

```text
/dev/ttyUSB0 root:plugdev 664
usuario en grupo plugdev
```

Prueba directa de protocolo:

```bash
PYTHONPATH=/home/andresrivera/digital_UN/tools/ws2812_studio \
/home/andresrivera/digital_UN/.venv-ws2812-studio/bin/python - <<'PY'
from ws2812_studio.services.device_controller import DeviceController
from ws2812_studio.services.serial_transport import SerialTransport

controller = DeviceController(SerialTransport("/dev/ttyUSB0", baudrate=115200, timeout=0.05))
controller.open()
print(controller.ping())
controller.close()
PY
```

Resultado real:

```text
OPEN /dev/ttyUSB0 115200: OK
PING: ERROR TimeoutError: Device did not respond
GET_INFO: ERROR TimeoutError: Device did not respond
```

Diagnostico:

```text
El FT232RL detectado esta conectado al header JTAG para programacion.
El UART del SoC LiteX no esta en esos pines: serial_tx=T6 y serial_rx=R7.
Por eso la FPGA se detecta/programa por JTAG, pero el firmware no responde por /dev/ttyUSB0.
```

Siguiente accion fisica necesaria: conectar un USB-UART real al UART LiteX
del bitstream, o exponer un UART del SoC en pines fisicamente accesibles sin
modificar WS2812, DMA, FSM, timing ni el pin C4.

No marcar PASS sin observacion fisica.

## Build & Program rojo

Proyecto:

```text
tools/ws2812_studio/build/red.ws2812project
1 frame rojo, 750 ms
```

Resultado:

```text
Generacion C: PASS
Firmware: PASS
Bitstream: PASS
Timing: 75.00 MHz PASS at 60.00 MHz
Deteccion FPGA: PASS
Programacion SRAM: PASS
```

Pendiente: confirmacion visual del usuario de que la matriz esta roja.
