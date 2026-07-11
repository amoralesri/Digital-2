# Auditoria de dependencias

Fecha local: 2026-07-10
Repositorio: `/home/andresrivera/digital_UN`

## Estado actual

Se creo y uso un entorno virtual local:

```text
/home/andresrivera/digital_UN/.venv-litex
```

El Python del sistema es `Python 3.14.4`. El entorno virtual permite regenerar LiteX, compilar firmware y ejecutar simulaciones SoC.

## Python FPGA instalado en `.venv-litex`

| Paquete | Origen | Version/commit observado | Estado |
| --- | --- | --- | --- |
| `migen` | `github.com/m-labs/migen.git` | `e19524c963a8342952840983047557707fbe0b6a` | PASS |
| `litex` | `github.com/enjoy-digital/litex.git` | `5de78e0bc06eec984e9ed8dd29f787ea6b666313` / 2026.4 | PASS |
| `litex-boards` | `github.com/litex-hub/litex-boards.git` | `30ea19b2d6130d35f1d9631a01f2166ad9ea7549` / 2026.4 | PASS |
| `litedram` | `github.com/enjoy-digital/litedram.git` | `d3011915f07e9d076e90b89219459da85d7cede4` / 2026.4 | PASS |
| `liteeth` | `github.com/enjoy-digital/liteeth.git` | `276c9e37fb4d92a5c0f30d39a51c20f42a59cf93` / 2026.4 | PASS |
| `litespi` | `github.com/litex-hub/litespi.git` | `8ca711b8e5c705c9502d6e8d162ae13f7c2fb128` / 2026.4 | PASS |
| `pythondata-cpu-vexriscv` | `litex-hub` | `642ecfed1c84460555d6d803d660cc60cfc1ecb6` | PASS |
| `pythondata-software-picolibc` | `litex-hub` | `6a13ccce7c575b32c102dd9dc52178505b81fe39` | PASS |
| `pythondata-software-compiler_rt` | `litex-hub` | `6eb76609c9627bf26635e57c63fb22cda7115887` | PASS |

Nota: `github.com/enjoy-digital/litespi.git` no existe; el origen usado fue `github.com/litex-hub/litespi.git`.

## Herramientas del sistema

| Herramienta | Version/salida relevante | Estado |
| --- | --- | --- |
| `iverilog` / `vvp` | Icarus Verilog 12.0 | PASS |
| `gtkwave` | presente | PASS |
| `yosys` | 0.52 | PASS |
| `nextpnr-ecp5` | 0.9-3 | PASS |
| `ecppack` | Project Trellis 1.4-3 | PASS |
| `openFPGALoader` | v0.13.1 | PASS |
| `riscv32-unknown-elf-gcc` | GCC 14.2.0 | PASS |
| `riscv64-unknown-elf-gcc` | GCC 14.2.0 | PASS |

## Comandos de verificacion

```bash
source /home/andresrivera/digital_UN/.venv-litex/bin/activate
python -c "import migen, litex, litex_boards, litedram, liteeth, litespi"
iverilog -V
yosys -V
nextpnr-ecp5 --version
openFPGALoader -V
riscv64-unknown-elf-gcc --version
```

## Uso recomendado

Desde `Litex/`, usar ruta absoluta para evitar problemas en Makefiles recursivos:

```bash
PYTHON=/home/andresrivera/digital_UN/.venv-litex/bin/python make sim_lattice_dma
```

Si se activa el venv y se usa `PYTHON=python`, tambien funciona desde el directorio raiz del target.

## Limitaciones

- `gw_sh` y herramientas Efinix `efx_*` no estan disponibles; los flujos Gowin/Efinix siguen fuera de alcance.
- `openFPGALoader` esta instalado, pero la deteccion fisica no encontro una cadena JTAG programable.
