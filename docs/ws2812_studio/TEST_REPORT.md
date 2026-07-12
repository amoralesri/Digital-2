# WS2812 Studio - Test Report

## Pruebas Python

Ejecutado desde:

```bash
cd tools/ws2812_studio
/home/andresrivera/digital_UN/.venv-ws2812-studio/bin/python -m pytest
```

Resultado:

```text
14 passed in 0.14s
```

Cobertura:

| Area | Archivo |
| --- | --- |
| Protocolo | `tests/test_protocol.py` |
| Mapeo | `tests/test_mapping.py` |
| Imagenes | `tests/test_image_converter.py` |
| Proyecto | `tests/test_project_serialization.py` |
| Simulador | `tests/test_simulated_integration.py` |

## Smoke test UI

Ejecutado con Qt en modo offscreen:

```bash
QT_QPA_PLATFORM=offscreen /home/andresrivera/digital_UN/.venv-ws2812-studio/bin/python - <<'PY'
from PySide6.QtWidgets import QApplication
from ws2812_studio.ui.main_window import MainWindow
app = QApplication([])
window = MainWindow()
print(window.windowTitle())
window.close()
PY
```

Resultado:

```text
WS2812 Studio
```

## Firmware

Compilado desde:

```bash
cd /home/andresrivera/digital_UN/Litex
BUILD_DIR=../build/colorlight_5a_75b_ws2812/ \
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python \
make -C NO_bios_fw_dma clean all
```

Resultado:

```text
ROM usage: 2.65KiB (4.14%)
SRAM usage: 0.46KiB (5.76%)
firmware.bin generado
```

## Bitstream

Regenerado para Colorlight 5A-75B V8.2 / LFE5U-25F-6BG256C:

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

Resultado final de timing:

```text
Fmax: 72.39 MHz
Target: 60.00 MHz
Slack minimo observado en histograma: >= 2.543 ns
Estado: PASS
```

## Validacion fisica 2026-07-12

FPGA detectada por JTAG:

```text
IDCODE: 0x41111043
Lattice ECP5 LFE5U-25
Codigo de retorno: 0
```

Programacion SRAM:

```text
Comando:
openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD Litex/build/colorlight_5a_75b_ws2812/gateware/colorlight_5a_75b.bit

Resultado:
Open file: DONE
Parse file: DONE
Enable configuration: DONE
SRAM erase: DONE
Loading: 100.00%
Done
Disable configuration: DONE
Codigo de retorno: 0
```

UART:

```text
Puerto host identificado: /dev/ttyUSB0
Adaptador: FT232RL A50285BI
Baud probado: 115200
PING: TimeoutError, sin respuesta
GET_INFO: TimeoutError, sin respuesta
```

Conclusion: la programacion JTAG funciona, pero la validacion WS2812 Studio
queda bloqueada porque el FT232RL conectado al header JTAG no esta cableado a
los pines UART del SoC (`serial_tx=T6`, `serial_rx=R7`).
