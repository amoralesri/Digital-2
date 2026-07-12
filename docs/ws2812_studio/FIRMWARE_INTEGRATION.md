# WS2812 Studio - Firmware Integration

Firmware modificado:

```text
Litex/NO_bios_fw_dma/main.c
```

La secuencia local de patrones se reemplazo por un parser UART por bytes. El
firmware conserva las funciones de control validadas:

```text
ws2812_load_framebuffer()
ws2812_show()
wait_until_loader_done()
wait_until_dma_done()
wait_until_ws2812_done()
```

## Comandos

`PING`, `GET_INFO`, `SET_FRAME`, `CLEAR`, `SET_BRIGHTNESS` y `STOP`.

## DMA

Para `SET_FRAME`:

1. Recibe 192 bytes RGB.
2. Valida longitud y CRC.
3. Llena 64 palabras del framebuffer.
4. Configura `disp0_dma_base`.
5. Configura `disp0_dma_length = 64 * 4`.
6. Activa DMA.
7. Dispara `disp0_init`.
8. Espera `disp0_done`.
9. Responde ACK/NACK.

El brillo se aplica en la aplicacion antes del envio para evitar doble escalado.

## UART

La app envia frames como 192 bytes RGB. El firmware valida SOF, version,
longitud y CRC16 antes de tocar el framebuffer.

El firmware responde siempre con `ACK` o `NACK` usando el mismo numero de
secuencia de la solicitud.
