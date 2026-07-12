# WS2812 Studio - User Guide

## Instalar

```bash
cd /home/andresrivera/digital_UN
python3 -m venv .venv-ws2812-studio
source .venv-ws2812-studio/bin/activate
python -m pip install --upgrade pip
python -m pip install -r tools/ws2812_studio/requirements.txt
```

## Ejecutar

```bash
PYTHONPATH=tools/ws2812_studio python -m ws2812_studio
```

o:

```bash
tools/ws2812_studio/run.sh
```

## Uso basico

1. Selecciona `Simulador` o `Dispositivo real`.
2. En modo real selecciona puerto y baud `115200`.
3. Conecta.
4. Ejecuta `PING`.
5. Ejecuta `GET_INFO`.
6. Dibuja en la matriz 8x8.
7. Presiona `Enviar frame`.
8. Activa `Live Sync` para enviar cambios automaticamente.
9. Usa el timeline para crear y reproducir frames.

## Imagenes

Usa `Importar imagen` para convertir PNG/JPG/BMP/WebP a un frame 8x8.

## Conexion fisica UART

El cable FT232RL usado para OpenFPGALoader esta conectado al header JTAG. Ese
enlace sirve para detectar y programar la FPGA, pero no garantiza comunicacion
con WS2812 Studio.

En el bitstream actual para Colorlight 5A-75B V8.2, LiteX genera el UART del
SoC en:

```text
serial_tx -> FPGA T6
serial_rx -> FPGA R7
baud      -> 115200
```

Para usar `Dispositivo real`, el USB-UART debe estar conectado al UART del SoC,
con tierra comun:

```text
USB-UART RX <- FPGA serial_tx T6
USB-UART TX -> FPGA serial_rx R7
GND comun
```

No confundir este UART con los pines JTAG usados por:

```text
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD
```
