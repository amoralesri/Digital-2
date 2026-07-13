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

1. Dibuja en la matriz 8x8.
2. Selecciona colores y brillo.
3. Usa el timeline para crear frames y duraciones.
4. Guarda el proyecto.
5. Presiona `COMPILAR Y PROGRAMAR`.
6. Confirma que la matriz tiene alimentacion segura y GND comun.
7. Espera el resultado del pipeline.

La FPGA reproduce la animacion de forma autonoma despues de programar SRAM.

## Imagenes

Usa `Importar imagen` para convertir PNG/JPG/BMP/WebP a un frame 8x8.

## Botones de build

| Boton | Funcion |
| --- | --- |
| `Guardar` | Guarda el proyecto editable |
| `Generar firmware` | Escribe `generated_animation.h/.c` |
| `Compilar` | Genera firmware y bitstream sin programar |
| `Programar FPGA` | Programa el bitstream existente en SRAM |
| `COMPILAR Y PROGRAMAR` | Ejecuta el flujo completo |

La consola de la derecha muestra etapa, progreso, salida tecnica y resultado.

## Live UART opcional

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

La falta de UART no impide usar Build & Program.
