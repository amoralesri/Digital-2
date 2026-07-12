# WS2812 Studio

Aplicacion de escritorio para editar y enviar frames a la matriz WS2812 8x8 del proyecto LiteX en Colorlight 5A-75B V8.2.

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

La aplicacion incluye modo simulador para desarrollar sin la FPGA conectada.
