# Validacion fisica WS2812

Fecha local: 2026-07-10
Estado: BLOCKED parcial. FPGA programada y matriz activa; faltan pruebas visuales finas.

## Actualizacion 2026-07-11 - Colorlight 5A-75B V8.2 programada

La placa objetivo queda fijada como:

```text
Colorlight 5A-75B V8.2
FPGA: LFE5U-25F-6BG256C
DIN matriz WS2812: J1 pin fisico 1
```

Correspondencia confirmada desde `litex_boards.platforms.colorlight_5a_75b`:

| Nivel | Valor |
| --- | --- |
| Revision LiteX | `8.2` |
| Tabla de conectores usada | `_connectors_v8_0` |
| Entrada de J1 | `"C4 D4 E4 - D3 F5 E3 N4 N5 N3 P3 P4 M3 N1 M4 -"` |
| Pin fisico J1.1 | primer elemento de la lista |
| Indice LiteX | `j1:0` |
| Pin FPGA real | `C4` |
| Constraint generado | `LOCATE COMP "ws28120_dout" SITE "C4";` |

Deteccion antes de programar:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

Resultado:

```text
Jtag probe limited to 3MHz
Jtag frequency : requested 6000000Hz -> real 3000000Hz
ret 0
idcode 0x41111043
manufacturer lattice
family ECP5
model LFE5U-25
```

Programacion SRAM ejecutada:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD -m build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
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

Codigo de retorno: `0`.

Bitstream cargado:

```text
Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```

Este bitstream fue regenerado con firmware de validacion lenta para hacer observables los pasos fisicos. El cierre temporal de esta imagen reporto:

```text
Max frequency for clock '$glbnet$crg_clkout0': 76.58 MHz (PASS at 60.00 MHz)
Critical path total: 13.06 ns
Slack setup aproximado: +3.61 ns
```

Estado de validacion visual:

| Prueba | Estado | Observacion |
| --- | --- | --- |
| a. Todos los LEDs apagados | BLOCKED | Pendiente confirmacion visual del usuario |
| b. LED 0 con brillo bajo | BLOCKED | Pendiente confirmacion visual del usuario |
| c. LED 63 con brillo bajo | BLOCKED | Pendiente confirmacion visual del usuario |
| d. Rojo | PASS parcial | Usuario reporta cambios de color visibles; falta confirmar orden exacto |
| e. Verde | PASS parcial | Usuario reporta cambios de color visibles; falta confirmar orden exacto |
| f. Azul | PASS parcial | Usuario reporta cambios de color visibles; falta confirmar orden exacto |
| g. Filas | BLOCKED | Pendiente confirmacion visual del usuario |
| h. Columnas | BLOCKED | Pendiente confirmacion visual del usuario |
| i. Ajedrezado | BLOCKED | Pendiente confirmacion visual del usuario |
| j. Barrido | PASS parcial | Usuario reporta efecto en cascada visible |
| k. Dos frames consecutivos | PASS parcial | Usuario reporta cambios intermitentes de color; falta confirmar reemplazo exacto |
| l. Ruta CSR | BLOCKED | Pendiente confirmacion visual del usuario |
| m. Ruta DMA | PASS parcial | Firmware usa ruta DMA y la matriz responde fisicamente |

Observacion fisica reportada por el usuario: toda la matriz se enciende, cambia colores intermitentemente muy rapido y se ve un efecto en cascada. A partir de esa observacion se regenero y programo una variante con pausas largas en firmware para permitir inspeccionar los pasos individuales. El firmware limita brillo inicial con `WS2812_BRIGHTNESS=0x10`. No se modificaron temporizacion WS2812, FSM, RTL, DMA ni CSR durante esta programacion.

## Actualizacion 2026-07-11 - deteccion JTAG confirmada

La FPGA ya fue detectada con el cable FT232RL usado como JTAG por bit-bang:

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect
```

Salida relevante:

```text
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

El adaptador aparece como:

```text
003 016 0x0403:0x6001 ft232RL FTDI A50285BI FT232R USB UART
```

El comando `openFPGALoader --detect` sin `-c ft232RL --pins=TXD:CTS:DTR:RXD` sigue fallando porque intenta una interfaz FT2232 por defecto. Para esta conexion el comando correcto es el de FT232RL con pines explicitos.

Estado fisico actual:

| Punto | Estado |
| --- | --- |
| FT232RL visible por USB | PASS |
| Cadena JTAG ECP5 detectada | PASS |
| Revision exacta PCB 5A-75B | PENDIENTE |
| Pin fisico DIN WS2812 | PENDIENTE |
| Bitstream 5A-75B con timing cerrado | PASS build |
| Programacion de FPGA | BLOCKED |
| Pruebas LED fisicas | BLOCKED |

No se ejecuto programacion porque el bitstream construido usa `j1:0` como pin temporal de DOUT. Antes de programar hay que confirmar el pin real conectado a DIN de la matriz y la revision impresa de la PCB.

## Actualizacion de deteccion actual

La inspeccion mas reciente no encontro ningun FTDI/JTAG conectado:

```text
lsusb
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 002: ID 1bcf:28cf Sunplus Innovation Technology Inc. Integrated_Webcam_FHD
Bus 003 Device 003: ID 0a5c:5843 Broadcom Corp. BCM58200 ControlVault 3
Bus 003 Device 004: ID 8087:0026 Intel Corp. AX201 Bluetooth
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub

openFPGALoader --scan-usb
empty
Bus device vid:pid       probe type      manufacturer serial               product

openFPGALoader --detect
empty
No cable or board specified: using direct ft2232 interface
unable to open ftdi device: -3 (device not found)
JTAG init failed with: unable to open ftdi device
```

`dmesg | tail -100` no pudo consultarse por permisos: `read kernel buffer failed: Operation not permitted`.

Ademas falta evidencia fisica para cerrar Colorlight 5A-75B: revision exacta de PCB, FPGA/paquete, oscilador, cadena JTAG y pin real conectado a DIN de la matriz WS2812. No se debe ejecutar `openFPGALoader -m` hasta resolver esos puntos.

## Deteccion ejecutada

```bash
lsusb
openFPGALoader --scan-usb
openFPGALoader --detect
openFPGALoader -V
```

Salidas relevantes:

```text
Bus 003 Device 009: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
```

```text
empty
Bus device vid:pid       probe type      manufacturer serial               product
003 009    0x0403:0x6001 ft232RL         FTDI         A50285BI             FT232R USB UART
```

```text
empty
No cable or board specified: using direct ft2232 interface
unable to open ftdi device: -3 (device not found)
JTAG init failed with: unable to open ftdi device
```

Version:

```text
openFPGALoader v0.13.1
```

## Interpretacion

- Hay un FT232R USB UART visible.
- No se confirmo una cadena JTAG/SPI programable.
- No se confirmo una Colorlight lista para programar.
- Por instruccion de seguridad, no se cargo el bitstream.

## Bitstream disponible, no programado

```text
Litex/build/colorlight_i5/gateware/colorlight_i5.bit
```

Este bitstream fue generado con RAM integrada y tiene warning de timing a 60 MHz. No debe tratarse como validacion fisica.

## Checklist antes de programar

| Punto | Estado |
| --- | --- |
| FPGA detectada inequivocamente | BLOCKED |
| Programador/cadena detectada | BLOCKED |
| Matriz WS2812 alimentada externamente | PENDIENTE |
| Tierra comun FPGA/matriz/fuente | PENDIENTE |
| Nivel logico de datos validado | PENDIENTE |
| Brillo limitado en firmware | PASS parcial |
| Timing FPGA cerrado | FAIL/WARNING |

## Comando de programacion esperado

Solo ejecutar despues de confirmar placa/cadena y seguridad electrica:

```bash
openFPGALoader -m Litex/build/colorlight_i5/gateware/colorlight_i5.bit
```

## Criterio de PASS fisico

La fase fisica solo puede marcarse PASS cuando:

- `openFPGALoader` detecte el target correcto.
- Se programe un bitstream aceptado.
- La matriz tenga fuente externa segura y GND comun.
- Se observen patrones rojo, verde, azul, blanco reducido, barrido, filas/columnas y una segunda actualizacion.
