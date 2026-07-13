# WS2812 Studio

Aplicacion de escritorio para editar animaciones de una matriz WS2812 8x8 y
programarlas en la Colorlight 5A-75B V8.2 por FT232RL/JTAG.

El modo principal no necesita UART:

```text
editar -> guardar proyecto -> compilar y programar -> FPGA reproduce autonomamente
```

## Ejecucion

```bash
cd /home/andresrivera/digital_UN
python3 -m venv .venv-ws2812-studio
source .venv-ws2812-studio/bin/activate
python -m pip install --upgrade pip
python -m pip install -r tools/ws2812_studio/requirements.txt
PYTHONPATH=tools/ws2812_studio python -m ws2812_studio
```

Tambien puedes usar:

```bash
tools/ws2812_studio/run.sh
```

## Build & Program

Desde la UI usa `COMPILAR Y PROGRAMAR`. Internamente ejecuta:

```bash
tools/ws2812_studio/scripts/build_and_program.py --project <archivo.ws2812project>
```

Genera:

```text
Litex/NO_bios_fw_dma/generated_animation.h
Litex/NO_bios_fw_dma/generated_animation.c
```

Cada LED se guarda como `0x00GGRRBB`. El bitstream se programa en SRAM, por lo
que se pierde al apagar la FPGA.

La aplicacion conserva el modo Live UART como opcion secundaria, pero no es
necesario para compilar ni programar.
