# Baseline del proyecto WS2812 LiteX

Fecha local de captura: 2026-07-10
Repositorio: `/home/andresrivera/digital_UN`
Rama original al iniciar: `main`
Rama de trabajo creada: `feat/ws2812-litex-final-project`
Commit base:

```text
ec35eca0afbb268bfbdd3a14c223f9266c3c88a8
```

## Comandos obligatorios ejecutados

```bash
pwd
git rev-parse --show-toplevel
git rev-parse HEAD
git status --short
git log --oneline -15
```

Resultados principales:

```text
pwd: /home/andresrivera/digital_UN
repo root: /home/andresrivera/digital_UN
HEAD: ec35eca0afbb268bfbdd3a14c223f9266c3c88a8
```

Ultimos commits:

```text
ec35eca0 Fixing some files
92e89198 updating files
d31e3116 Adding dma firmware version
de82fc87 fixing ws2812/ws2812_streamer.py working DMA transfer
06d9ea57 Working ws2812 with stream simulation
a40dc3bd Adding ws2812_streamer simulation
91c94c5d Adding litex stream
0d1ba2be fixing Makefile
21355607 restoring demo
12c3e0ba Fixing litex simulation
c042cd2f Fixing no bios simulation
14b576ce fixing Litex
fc7a3c9d Adding no bios version, and simulation with lattice
de2452b8 Adding write led mem simulation
df678ddc Adding missing files
```

## Estado inicial del arbol de trabajo

El arbol no estaba limpio antes de iniciar esta tarea. Estos cambios se consideran preexistentes y no deben descartarse sin revision:

```text
 M Litex/board/colorlight_i5.py
 M Litex/colorlight_i5.py
 M Litex/csr.csv
 M Litex/firmware/helpers.c
 M Litex/firmware/main.c
?? CONTEXTO_REPOSITORIO.md
?? Litex/NO_bios_fw/firmware.bin
?? Litex/board/__pycache__/colorlight_i5.cpython-314.pyc
?? Litex/build/
?? Litex/firmware/crt0.d
?? Litex/firmware/crt0.o
?? Litex/firmware/firmware.bin
?? Litex/firmware/firmware.elf
?? Litex/firmware/helpers.d
?? Litex/firmware/helpers.o
?? Litex/firmware/isr.d
?? Litex/firmware/isr.o
?? Litex/firmware/main.d
?? Litex/firmware/main.o
?? Litex/mult/__pycache__/mult_32.cpython-314.pyc
?? Litex/reporte_comparacion_pull_simulacion.md
?? Litex/reporte_diagnostico_simulacion_calculadora.md
?? Litex/ws2812/__pycache__/
?? femtoRV/basic/rtl/cores/ws2812/a.out
?? femtoRV/basic/rtl/cores/ws2812/ws2812_led_TB.vcd
```

Resumen de cambios trackeados preexistentes:

```text
Litex/board/colorlight_i5.py |   3 +-
Litex/colorlight_i5.py       |   1 -
Litex/csr.csv                | 158 ++++++++++++++++++++++---------------------
Litex/firmware/helpers.c     |   2 +-
Litex/firmware/main.c        | 138 ++++++++++++++++++++++++-------------
5 files changed, 175 insertions(+), 127 deletions(-)
```

## Estructura principal del repositorio

```text
Embedded/
Litex/
basic_circuits/
docs/
femtoRV/
migen_tutorial/
```

Subcarpetas relevantes ya existentes para este proyecto:

```text
Litex/
Litex/NO_bios_fw/
Litex/NO_bios_fw_dma/
Litex/board/
Litex/build/
Litex/firmware/
Litex/lattice_sim/
Litex/mult/
Litex/ws2812/
femtoRV/basic/rtl/cores/ws2812/
basic_circuits/test_peripherals/rtl/cores/test/ws2812/
```

## Politica de proteccion

- No se descartaran cambios locales preexistentes.
- No se editaran archivos generados dentro de `build/**` como solucion permanente.
- No se editaran manualmente `csr.h`, `soc.h`, `regions.ld`, gateware generado ni `.init` generados.
- No se modificara `VexRiscv.v`.
- No se modificaran multiplicador, divisor, FemtoRV, panel LED 12 bpp u otros perifericos salvo dependencia real demostrada.
- La validacion fisica quedara marcada como pendiente si no se detecta hardware y matriz disponibles.

## Siguiente fase

La siguiente fase es la auditoria completa de dependencias y herramientas antes de implementar cualquier cambio RTL/Migen/firmware.
