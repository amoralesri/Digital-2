# WS2812 Studio - Development

## Tests

```bash
cd /home/andresrivera/digital_UN/tools/ws2812_studio
/home/andresrivera/digital_UN/.venv-ws2812-studio/bin/python -m pytest
```

## Estructura

```text
ws2812_studio/models      modelos de frame, animacion y proyecto
ws2812_studio/services    codegen, pipeline, protocolo, transporte, mapeo, imagenes
ws2812_studio/ui          widgets PySide6
tests                     pruebas automatizadas
scripts                   entrada CLI del pipeline Build & Program
```

## Generacion de animacion

```bash
cd /home/andresrivera/digital_UN
PYTHONPATH=tools/ws2812_studio \
.venv-ws2812-studio/bin/python tools/ws2812_studio/scripts/build_and_program.py \
  --project tools/ws2812_studio/build/red.ws2812project \
  --no-program
```

La UI invoca este pipeline con `QProcess`, de modo que la ventana no queda
bloqueada durante Yosys/nextpnr.

## Firmware

Compilar con headers del target 5A-75B:

```bash
cd /home/andresrivera/digital_UN/Litex
BUILD_DIR=../build/colorlight_5a_75b_ws2812/ \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make -C NO_bios_fw_dma clean all
```

## Bitstream

```bash
cd /home/andresrivera/digital_UN/Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_5a_75b_ws2812_dma.py \
  --revision=8.2 \
  --device-override=LFE5U-25F-6BG256C \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

## App

```bash
cd /home/andresrivera/digital_UN/tools/ws2812_studio
./run.sh
```

El modo simulador permite probar PING, GET_INFO y envio de frames sin conectar
la FPGA.

## Dependencias externas

```text
riscv64-unknown-elf-gcc
yosys
nextpnr-ecp5
ecppack
openFPGALoader
LiteX en .venv-litex
```

## Programacion SRAM

```bash
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD \
  Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit
```
