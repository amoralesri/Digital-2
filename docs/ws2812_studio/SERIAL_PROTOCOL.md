# WS2812 Studio - Serial Protocol

## Packet Format

```text
SOF          2 bytes: 0xA5 0x5A
VERSION      1 byte : 0x01
COMMAND      1 byte
SEQUENCE     2 bytes little-endian
LENGTH       2 bytes little-endian
PAYLOAD      LENGTH bytes
CRC16        2 bytes little-endian
```

CRC: CRC16-CCITT, inicial `0xffff`, calculado sobre:

```text
VERSION + COMMAND + SEQUENCE + LENGTH + PAYLOAD
```

## Commands

| Codigo | Nombre | Payload |
| --- | --- | --- |
| `0x01` | `PING` | vacio |
| `0x02` | `GET_INFO` | vacio |
| `0x10` | `SET_FRAME` | 192 bytes RGB |
| `0x11` | `CLEAR` | vacio |
| `0x12` | `SET_BRIGHTNESS` | 1 byte |
| `0x13` | `STOP` | vacio |
| `0x7e` | `ACK` | comando original, estado, mensaje |
| `0x7f` | `NACK` | comando original, estado, mensaje |

## SET_FRAME

Payload:

```text
64 pixeles * 3 bytes = 192 bytes
R, G, B por pixel
```

La aplicacion aplica brillo y mapeo logico a fisico antes de enviar. El firmware recibe el frame fisico, llena el framebuffer en SRAM y dispara la ruta DMA validada.

## ACK/NACK

Payload minimo:

```text
byte 0: comando original
byte 1: codigo de estado
byte 2..n: mensaje ASCII corto opcional
```

Estados:

| Codigo | Nombre |
| --- | --- |
| `0` | `OK` |
| `1` | `CRC_ERROR` |
| `2` | `INVALID_LENGTH` |
| `3` | `UNKNOWN_COMMAND` |
| `4` | `DEVICE_BUSY` |
| `5` | `DMA_TIMEOUT` |
| `6` | `WS2812_TIMEOUT` |
| `7` | `PROTOCOL_VERSION_ERROR` |
