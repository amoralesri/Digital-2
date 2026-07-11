# Contexto completo del repositorio `digital_UN`

> Actualizacion oficial 2026-07-10, cierre WS2812 64 LEDs: la rama activa es `feat/ws2812-litex-final-project`. Se verifico RTL WS2812 de 64 LEDs con `LED63` incluido y sin `LED64`, CSR directo con 64 escrituras, DMA con 64 palabras de 32 bits por frame y dos frames consecutivos. El build preliminar `colorlight_i5` con RAM integrada genera bitstream, pero la corrida fresca de nextpnr queda en `57.02 MHz (FAIL at 60.00 MHz)`. La placa final solicitada es Colorlight 5A-75B, pero sigue bloqueada hasta confirmar revision fisica, FPGA/paquete, oscilador, JTAG y pin WS2812. No se programo FPGA.

> Actualizacion 2026-07-10 posterior al cierre WS2812: el trabajo activo ya no esta en `main`, sino en la rama `feat/ws2812-litex-final-project`. La documentacion tecnica vigente del cierre WS2812 esta en `README_WS2812.md` y `docs/ws2812/`. En esta segunda ronda se creo `.venv-litex`, se regeneraron SoC/CSR/headers, se compilaron firmwares no-BIOS, se verifico `sim_lattice_dma` reducido, se genero bitstream con RAM integrada y se dejo documentado que falta cerrar timing fisico y confirmar JTAG antes de programar FPGA. El bloque historico siguiente queda como inventario general generado antes de esta continuacion.

Fecha de generacion local: 2026-07-10 20:02:22 -05
Ruta local inspeccionada: `/home/andresrivera/digital_UN`
Remoto Git: `https://github.com/cicamargoba/digital_UN.git`
Rama actual: `main`
HEAD actual: `ec35eca0 Fixing some files`

Este documento resume el estado actual del repositorio para que una persona nueva pueda entender que contiene, que flujos de trabajo existen, que cambios recientes se integraron y que modificaciones locales quedan pendientes.

## Resumen ejecutivo

`digital_UN` es un repositorio de diseno digital y sistemas embebidos usado como banco de practicas, ejemplos y experimentos de FPGA/SoC. Combina:

- Circuitos digitales basicos en Verilog y archivos `.dig`.
- SoC basados en FemtoRV/RISC-V con firmware en C y ensamblador.
- Perifericos de prueba: multiplicador, divisor, raiz cuadrada, conversion binario/BCD, RAM, UART, WS2812 y paneles LED.
- Integraciones Migen/LiteX para construir SoC, generar CSR, simular y programar FPGAs.
- Flujos de sintesis/simulacion para Lattice ECP5, Gowin Tang, Efinix y algunos ejemplos iCE40.
- Un arbol grande de Buildroot/YuzukiSBC para sistemas Linux embebidos.
- Documentacion PDF y reportes locales de diagnostico.

El repositorio esta organizado como material de aprendizaje y desarrollo iterativo. Hay codigo fuente, testbenches, archivos de forma de onda GTKWave, bitstreams o artefactos generados en algunas carpetas, scripts de imagen, firmware precompilado y Makefiles por proyecto.

## Estado Git actual

El repositorio local esta sincronizado con `origin/main` en el commit:

```text
ec35eca0 (HEAD -> main, origin/main, origin/HEAD) Fixing some files
```

El ultimo pull trajo 9 commits desde el estado anterior `12c3e0ba` hasta `ec35eca0`:

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
```

Quedan cambios locales sin commit en archivos trackeados:

```text
M Litex/board/colorlight_i5.py
M Litex/colorlight_i5.py
M Litex/csr.csv
M Litex/firmware/helpers.c
M Litex/firmware/main.c
```

Resumen de esos cambios locales:

```text
5 files changed, 175 insertions(+), 127 deletions(-)
```

Tambien existen archivos no trackeados/generados, principalmente builds, binarios, objetos, caches Python, reportes Markdown y trazas de simulacion:

```text
Litex/NO_bios_fw/firmware.bin
Litex/board/__pycache__/colorlight_i5.cpython-314.pyc
Litex/build/
Litex/firmware/*.d
Litex/firmware/*.o
Litex/firmware/firmware.bin
Litex/firmware/firmware.elf
Litex/mult/__pycache__/mult_32.cpython-314.pyc
Litex/reporte_comparacion_pull_simulacion.md
Litex/reporte_diagnostico_simulacion_calculadora.md
Litex/ws2812/__pycache__/
femtoRV/basic/rtl/cores/ws2812/a.out
femtoRV/basic/rtl/cores/ws2812/ws2812_led_TB.vcd
```

Hay un stash antiguo conservado:

```text
stash@{0}: On main: codex-before-pull-2026-06-16
```

## Tamano y composicion

Archivos trackeados totales: `15195`.

Distribucion por carpetas principales:

```text
Embedded        13055
Litex             469
basic_circuits    707
docs               10
femtoRV           655
migen_tutorial    298
```

Extensiones mas frecuentes:

```text
3052 mk
2913 hash
2893 in
2648 patch
 715 v
 370 py
 199 png
 147 txt
 120 c
 119 gtkw
 106 host
  84 service
  68 html
  67 config
  58 h
  52 vh
```

La alta cantidad de archivos `.mk`, `.in`, `.hash`, `.patch` y similares proviene principalmente del arbol `Embedded/Buildroot-YuzukiSBC/buildroot`.

## Mapa de carpetas principales

### `README.md`

README principal del repositorio. Describe el objetivo general: ejemplos y practicas de diseno digital con programas RISC-V y modulos Verilog. Indica requisitos basicos en Linux:

- `iverilog`
- `gtkwave`
- `make`
- `build-essential`
- `gcc-riscv64-unknown-elf`

Tambien documenta el uso basico de firmware en ensamblador dentro de `femtoRV/basic/firmware/asm` y simulacion RTL con `femtoRV/basic/rtl`.

### `basic_circuits/`

Material base de diseno digital. Contiene circuitos simples, ejemplos Verilog, testbenches y flujos FPGA.

Subcarpetas importantes:

- `basic_circuits/Digital/`: archivos `.dig` para circuitos didacticos como registros, latches, flip-flops, acumuladores y shifts.
- `basic_circuits/Verilog/`: modulos Verilog basicos y testbenches: `half_adder`, `acc`, `comp`, `control_mult`, `lsr`, `blink`, entre otros. Incluye Makefile para simulacion, post-sintesis y SVG.
- `basic_circuits/Blink/`: ejemplo de parpadeo con constraints y Makefile para varias placas/tecnologias: Lattice, Efinix, Gowin, iCEBreaker, Altera.
- `basic_circuits/test_peripherals/`: SoC de prueba con firmware C/ASM y perifericos en RTL. Incluye cores como `mult_ASM`, `divider_ASM`, `sqrt_ASM`, `dpRAM`, `bin2bcd`, `bcd2bin`, `led_panel`, `Panel_LED_48bpp`, `PWM_LED_panel` y `ws2812`.

Flujos tipicos:

```bash
cd basic_circuits/Verilog
make sim
make sim_post_syn
make svg
make clean
```

```bash
cd basic_circuits/Blink
make sim
make configure_lattice
make configure_i5
make configure_tang_primer_25k
make clean
```

### `femtoRV/`

Zona de SoC RISC-V basada en FemtoRV. Contiene firmware, RTL, testbenches, cores perifericos y simulaciones.

Subcarpetas importantes:

- `femtoRV/basic/`: flujo principal de SoC FemtoRV.
- `femtoRV/basic/firmware/asm/`: programas en ensamblador RISC-V, por ejemplo `calculator.S`, `mult.S`, `div.S`, `sqrt.S`, `bin2bcd.S`, `bcd2bin.S`, `for.S`, rutinas `getchar`, `putchar`, `putstring`, etc.
- `femtoRV/basic/firmware/c/`: firmware C y libreria `libfemtorv`.
- `femtoRV/basic/rtl/`: top `SOC.v`, variantes `SOC_flash.v`, testbenches, constraints y Makefile de simulacion/sintesis/programacion.
- `femtoRV/basic/rtl/cores/`: perifericos y bloques RTL reutilizables: CPU, UART, multiplicador, divisor, sqrt, RAM, conversiones BCD/binario, panel LED, PWM y WS2812.
- `femtoRV/litex/my_bios/`: BIOS/firmware estilo LiteX con `boot.c`, `readline`, helpers y linker.
- `femtoRV/simulation/`: simulaciones independientes del SoC FemtoRV.

Makefile principal revisado: `femtoRV/basic/rtl/Makefile`.

Targets relevantes:

```bash
make sim_quark
make sim_quark_flash
make sim_verilator
make sim_post_syn_quark
make sim_post_syn_quark_efx
make svg
make configure_lattice
make configure_i5
make configure_i9
make configure_icebreaker
make configure_tang_nano_20k
make configure_tang_primer_25k
make clean
```

El SoC `SOC` integra CPU FemtoRV Quark, UART y varios perifericos: multiplicador, divisor, raiz cuadrada, conversion binario/BCD, BCD/binario y BRAM. Tambien hay variantes con SPI flash.

### `Litex/`

Zona central de experimentos LiteX/Migen actuales. Es la parte mas activa del repo en el estado reciente.

Contiene:

- SoC para Colorlight i5/i9.
- Plataformas/boards locales.
- Firmware C con BIOS y sin BIOS.
- Perifericos Migen/LiteX y Verilog.
- Multiplicador como periferico CSR.
- WS2812 y streamer con DMA.
- Panel LED 12 bpp.
- Modelos de simulacion Lattice.
- Testbenches Verilog, `.gtkw`, `.init`, bitstreams y artefactos de build.

Archivos/carpeta clave:

- `Litex/Makefile`: flujo principal de build/simulacion LiteX.
- `Litex/colorlight_i5.py`: SoC Colorlight con LiteX, SDRAM, SPI flash, periferico WS2812 y DMA.
- `Litex/colorlight_i5_no_bios.py`: variante no-BIOS.
- `Litex/colorlight_i5_no_bios_dma.py`: variante no-BIOS con WS2812 conectado a DMA.
- `Litex/board/colorlight_i5.py`: plataforma local Colorlight i5/i9 y definicion de pines.
- `Litex/csr.csv`: mapa CSR generado/actual usado por firmware y diagnostico.
- `Litex/colorlight_i5_TB.v`: testbench principal.
- `Litex/colorlight_i5_dma_TB.v`, `colorlight_i5_dma_pc_TB.v`, `colorlight_i5_dma_reader_TB.v`: testbenches agregados para DMA.
- `Litex/lattice_sim/`: modelos Lattice/ECP5 para simulacion post-sintesis o gateware generado.

Targets principales de `Litex/Makefile`:

```bash
cd Litex
make fw_no_bios
make sim_lattice
make sim_lattice_dma
make sim_efinix
make svg
make litex_term
make clean
```

`sim_lattice` prepara firmware no-BIOS, genera headers LiteX/CSR, compila firmware, regenera SoC en modo simulacion, copia `.init`, corre `iverilog`, ejecuta `vvp` y abre GTKWave.

`sim_lattice_dma` hace un flujo parecido pero usando `colorlight_i5_no_bios_dma.py` y `NO_bios_fw_dma/`, con foco en transferencia DMA hacia el display WS2812.

#### `Litex/mult/`

Periferico multiplicador de 32 bits y entorno de prueba.

Contiene:

- `mult_32.py`: wrapper Migen/LiteX con CSR.
- `mult_32.v`: top Verilog.
- `control_mult.v`, `acc.v`, `comp.v`, `lsr_mult.v`, `rsr.v`: FSM/datapath.
- `mult_32_TB.v`, `perip_mult_32_TB.v`: testbenches.
- `.gtkw`: vistas GTKWave.

CSR expuestos por el wrapper:

- `_A`: operando A de 16 bits.
- `_B`: operando B de 16 bits.
- `_init`: pulso de inicio.
- `_pp`: producto de 32 bits.
- `_done`: finalizacion.

Targets:

```bash
cd Litex/mult
make sim
make sim_per
make sim_post_syn
make sim_post_syn_sky
make sim_post_route
make svg
make clean
```

#### `Litex/ws2812/`

Controlador WS2812, arreglo de LEDs y periferico LiteX.

Contiene:

- Bloques basicos: `ws2812.v`, `ctrl_ws.v`, `count_ws.v`, `mux_ws.v`.
- LED individual/arreglo: `ws2812_led.v`, `ws2812_led_array.v`, `led_mem*`, `ctrl_ws_arr.v`, `count_addr.v`.
- Periferico: `ws2812_periph.v`, `ws2812.py`.
- Streamer/DMA reciente: `ws2812_streamer.py`, `generate_ws2812_streamer_verilog.py`, `ws2812_streamer_generated.v`, testbenches y vistas GTKWave.

Targets:

```bash
cd Litex/ws2812
make sim
make streamer_v
make sim_streamer
make sim_streamer_view
make sim_post_syn
make svg
make configure_lattice
make clean
```

El streamer reciente usa un endpoint LiteX `stream.Endpoint([("data", 32)])`, acepta datos desde `WishboneDMAReader`, convierte el formato de palabra DMA a RGB y escribe la memoria del periferico WS2812.

#### `Litex/NO_bios_fw/` y `Litex/NO_bios_fw_dma/`

Firmware C para ejecutar sin BIOS, arrancando desde ROM inicializada.

`NO_bios_fw/` contiene firmware no-BIOS base.
`NO_bios_fw_dma/` fue agregado en los commits recientes y contiene firmware para la version con DMA.

Ambos incluyen:

- `Makefile`, variantes antiguas y ROM.
- `main.c`, `main_ok.c`, `main_old.c`, `main_sram.c`.
- `helpers.c/.h`, `uart.c`, `isr.c`, `readline.h`, `sample.h`.
- `linker.ld` y variantes.

`NO_bios_fw_dma/hello_world/` contiene un ejemplo separado con `main.c`, `isr.c`, `linker.ld`, listados y mapa ELF.

#### `Litex/firmware/`

Firmware C para flujo LiteX con BIOS/carga. Incluye:

- `Makefile`
- `main.c`
- `helpers.c/.h`
- `uart.c`
- `isr.c`
- `linker.ld`
- binarios/objetos generados locales como `firmware.bin`, `firmware.elf`, `.o`, `.d`.

Actualmente `Litex/firmware/main.c`, `helpers.c` y archivos relacionados tienen cambios locales sin commit.

#### `Litex/Led_panel_12bpp/`

Proyecto de panel LED de 12 bpp.

Contiene:

- RTL: `led_panel_4k.v`, `ctrl_lp4k.v`, `memory.v`, `memory_V2.v`, `mux_led.v`, `lsr_led.v`, etc.
- Wrapper Migen/Python: `led_panel_4k.py`.
- Testbench y GTKWave: `led_panel_4k_TB.v`, `led_panel_4k_sim.gtkw`.
- Imagenes y conversiones: `images/gen_image_128x32.py`, `images/image_to_raw.py`, PNG/JPG/WEBP de prueba.
- Hex de imagen: `image.hex`, `image0.hex`, `image1.hex`, `image_test.hex`.
- Constraints Gowin: `sipeed_tang_primer_25k.cst`, `.sdc`.
- Artefactos Gowin en `impl/`.

`images/gen_image_128x32.py` usa PIL/Numpy para convertir una imagen 128x128 al formato de memoria esperado por el panel: recorre 32 filas x 128 columnas, combina dos pixeles verticales y emite 3 bytes por linea en `../image.hex`.

#### `Litex/udp_transfer/`

Firmware y Makefile para transferencia UDP. Contiene `main.c`, `helpers`, `isr`, `start.S`, linker y listados generados.

#### `Litex/images/`

Imagenes y scripts de conversion reutilizados para pruebas visuales: banderas, personajes, conversiones a crudo/hex y logs de descarga.

### `migen_tutorial/`

Conjunto de tutoriales y prototipos Migen/LiteX.

Subcarpetas importantes:

- `blink/`: ejemplo LED/PWM con plataforma Efinix/Gowin.
- `pwm/`: periferico PWM.
- `uart/` y `uart_verilog/`: UART con Python/Migen y Verilog.
- `mult/`: version tutorial del multiplicador con firmware `mult_fw`.
- `cpu/`: SoC LiteX pequeno con CPU, Ethernet, PWM y firmware.
- `litescope/`: ejemplo con LiteScope/analyzer.
- `DMA_cpu/`: proyecto avanzado con CPU, HyperRAM, Ethernet, SPI ADC, DMA y subida por UDP.
- `Ether_Bridge/`, `Uart_Bridge/`: bridges/experimentos de comunicacion.
- `board/`: plataformas locales.

#### `migen_tutorial/DMA_cpu/`

Proyecto importante de SoC con DMA.

Contiene:

- `base.py`, `base_WR_RD_DMA.py`, `base_no_bios.py`: SoC en LiteX/Migen.
- `modules/SPIADCWithDMA.py`: modulo SPI ADC con DMA.
- `ver_modules/`: modulos Verilog para ADC, DPRAM, memory writer, register bank y SPI.
- `firmware/`, `no_bios_firmware/`, `stream_firmware/`, `NO_bios_firmware_stream/`: variantes de firmware.
- `remote_client/`, `udp_listener.py`, `plot_udp.py`, `test_dma_udp.py`: herramientas de prueba por red/UDP.
- `Docs/SoC.md`, `Docs/SPIDMA.md`, `Docs/DMAupload.md`: diagramas Mermaid del SoC, SPI DMA y subida DMA/UDP.

El diseno documentado integra:

- CPU LiteX.
- HyperRAM como memoria principal.
- LiteEth/Etherbone.
- SPI ADC.
- `WishboneDMAWriter` para escritura a memoria.
- `WishboneDMAReader` para lectura y envio UDP.
- FIFO y conversiones stream.

Targets principales:

```bash
cd migen_tutorial/DMA_cpu
make
make sim
make sim_quark
make sim_quark_flash
make sim_post_syn_quark
make svg
make configure
make configure_lattice
make configure_i5
make configure_efinix
make litex_term
make clean
```

#### `migen_tutorial/cpu/`

SoC LiteX pequeno. Tiene `base.py`, `platforms.py`, firmware, `csr.csv`, `load.py` y pruebas. En los commits recientes se agrego `migen_tutorial/cpu/platforms.py`.

### `Embedded/`

Arbol de sistemas embebidos Linux.

Subcarpetas:

- `Embedded/Buildroot-YuzukiSBC/`: copia grande de Buildroot/YuzukiSBC para Allwinner F1C100s/F1C200s/V3s/V3x/D1-H/D1s/T113/H616.
- `Embedded/patch_uboot/`: parches y DTS/defconfig para U-Boot.
- `Embedded/v1.0.1.tar.gz`: archivo comprimido local/trackeado.

El README de YuzukiSBC indica flujo:

```bash
cd Embedded/Buildroot-YuzukiSBC
source envsetup.sh
lunch
make yuzukihd_yuzukiruler_defconfig
make
```

Esta zona es mucho mas grande que el resto del repo y explica la mayoria de archivos trackeados.

### `docs/`

Documentos PDF de referencia:

- `Tema_1.pdf` a `Tema_5.pdf`
- `FPGA Ignite Yosys Course 2023-08-02-3.pdf`
- datasheets de paneles/display: `DP5020B-DP.pdf`, `datasheet-DP32020A-*`, `datasheet-DP3264S-chinese.pdf`

## Cambios recientes integrados desde el remoto

El ultimo pull desde `origin/main` actualizo 61 archivos:

```text
61 files changed, 241734 insertions(+), 42960 deletions(-)
```

Temas principales:

1. Se agrego una variante de firmware no-BIOS con DMA: `Litex/NO_bios_fw_dma/`.
2. Se agrego `Litex/colorlight_i5_no_bios_dma.py`.
3. Se agregaron testbenches y vistas para DMA: `colorlight_i5_dma_TB.v`, `colorlight_i5_dma_pc_TB.v`, `colorlight_i5_dma_reader_TB.v`, `colorlight_i5_dma.gtkw`, `colorlight_i5_no_bios_dma_sim.gtkw`.
4. Se agrego `Litex/ws2812/ws2812_streamer.py` y archivos generados/de prueba para el streamer WS2812.
5. Se ajusto `Litex/Makefile` con targets para simulacion DMA.
6. Se agregaron modelos de simulacion Lattice: `Litex/lattice_sim/cells_ff.v`, `Litex/lattice_sim/mult18x18d.v`.
7. Se agrego un `colorlight_i5_synth.v` grande como salida sintetizada.
8. Se eliminaron varios artefactos antiguos de `Litex/ws2812/DEMO_ws2812_led_array.*` como bitstream, reportes, SVF y synth log.
9. Se agrego `migen_tutorial/cpu/platforms.py`.

Archivos agregados destacados:

```text
Litex/NO_bios_fw_dma/*
Litex/colorlight_i5_no_bios_dma.py
Litex/colorlight_i5_dma*.v
Litex/colorlight_i5_dma*.gtkw
Litex/femtorv32_gracilis.v
Litex/lattice_sim/cells_ff.v
Litex/lattice_sim/mult18x18d.v
Litex/ws2812/generate_ws2812_streamer_verilog.py
Litex/ws2812/ws2812_streamer.py
Litex/ws2812/ws2812_streamer_generated*.v
migen_tutorial/cpu/platforms.py
```

## Reportes locales existentes

Hay dos reportes Markdown locales no trackeados en `Litex/`:

- `Litex/reporte_comparacion_pull_simulacion.md`
- `Litex/reporte_diagnostico_simulacion_calculadora.md`

El primero compara el pull anterior `fc7a3c9d..12c3e0ba` y explica la correccion del flujo de simulacion LiteX no-BIOS.

El segundo diagnostica la simulacion de calculadora/multiplicador LiteX, separando:

- SoC LiteX.
- Firmware con BIOS vs no-BIOS.
- Linker scripts y regiones de memoria.
- Inicializacion `.init`.
- Testbench.
- CSR del multiplicador.
- Posibles causas de fallos de simulacion.

Como no estan trackeados, existen solo en el arbol local actual salvo que se agreguen al repositorio.

## Flujos de trabajo por objetivo

### Simular circuitos Verilog simples

```bash
cd basic_circuits/Verilog
make sim
```

Abre GTKWave con las trazas definidas por el testbench.

### Simular el SoC FemtoRV basico

```bash
cd femtoRV/basic/rtl
make sim_quark
```

Genera y abre `bench.vcd`.

### Compilar firmware RISC-V ASM

```bash
cd femtoRV/basic/firmware/asm
make
```

El README principal indica que se suelen ajustar variables como `OBJECTS` y `OBJS` dentro del Makefile para elegir el programa `.S` que se desea compilar.

### Probar multiplicador LiteX aislado

```bash
cd Litex/mult
make sim
make sim_per
```

`sim` prueba el modulo `mult_32` como bloque RTL.
`sim_per` prueba el wrapper de periferico.

### Simular SoC LiteX no-BIOS

```bash
cd Litex
make sim_lattice
```

Este flujo genera firmware no-BIOS y prepara `.init` para la simulacion RTL con `iverilog`.

### Simular SoC LiteX no-BIOS con DMA hacia WS2812

```bash
cd Litex
make sim_lattice_dma
```

Este es el flujo mas reciente. Usa `colorlight_i5_no_bios_dma.py`, `NO_bios_fw_dma/` y `ws2812_streamer.py`.

### Generar y simular streamer WS2812

```bash
cd Litex/ws2812
make streamer_v
make sim_streamer
make sim_streamer_view
```

### Programar FPGAs

Hay varios targets por placa y tecnologia:

- `configure_lattice`
- `configure_i5`
- `configure_i9`
- `configure_sugar`
- `configure_icebreaker`
- `configure_tang_nano_20k`
- `configure_tang_primer_25k`
- `configure_efinix`

Los Makefiles usan herramientas como:

- `openFPGALoader`
- `yosys`
- `nextpnr-ecp5`
- `nextpnr-ice40`
- `ecppack`
- `icepack`
- `iceprog`
- `gw_sh`
- herramientas Efinix/Efinity

## Herramientas esperadas

Segun README y Makefiles, el repo asume disponibilidad de:

- Git.
- GNU Make.
- Python 3.
- Icarus Verilog: `iverilog`, `vvp`.
- GTKWave.
- Yosys.
- netlistsvg.
- Toolchains RISC-V bare-metal: `riscv32-unknown-elf-*` o symlinks desde `riscv64-unknown-elf-*`.
- LiteX/Migen y paquetes asociados cuando se trabaja en `Litex/` o `migen_tutorial/`.
- OpenFPGALoader.
- NextPNR/ECP5, IceStorm, Trellis segun placa.
- Gowin IDE para Tang.
- Efinix/Efinity para flujos Efinix.
- PIL/Pillow y Numpy para scripts de imagen.

## Notas importantes para nuevos lectores

1. No todo lo que existe en el arbol es fuente limpia. Hay artefactos generados trackeados y no trackeados: `.bit`, `.json`, `.vcd`, `.o`, `.d`, `.elf`, `.bin`, `.gtkw`, outputs Gowin/Efinix, etc.
2. `Embedded/Buildroot-YuzukiSBC/` domina el tamano del repo; no confundir ese arbol con los proyectos FPGA principales.
3. `Litex/` es la zona mas activa para el trabajo reciente de SoC Colorlight, multiplicador, WS2812 y DMA.
4. `femtoRV/basic/rtl/` es el flujo pedagogico de SoC FemtoRV con perifericos ASM/RTL.
5. Existen multiples copias de archivos generados LiteX (`csr.csv`, `.init`, build dirs). Para depurar simulacion, verificar siempre desde que directorio se ejecuta `vvp` y que `.init` esta leyendo.
6. Los Makefiles contienen rutas locales absolutas antiguas como `/home/carlos/...` o `/Work/CAD/...` para Efinity/Gowin. Es posible que deban ajustarse en otra maquina.
7. Antes de hacer commits conviene decidir que hacer con los archivos generados y no trackeados.
8. Los cambios locales actuales en `Litex/firmware/main.c`, `helpers.c`, `csr.csv` y archivos Colorlight pueden ser trabajo en progreso; no deben descartarse sin revisar.

## Punto de entrada recomendado

Para entender el repositorio en orden:

1. Leer `README.md`.
2. Revisar `basic_circuits/Verilog` para bloques RTL simples.
3. Revisar `femtoRV/basic/rtl/Makefile` y `femtoRV/basic/firmware/asm`.
4. Revisar `Litex/Makefile`.
5. Revisar `Litex/colorlight_i5.py` y `Litex/colorlight_i5_no_bios_dma.py`.
6. Revisar `Litex/mult/` si el foco es multiplicador/CSR.
7. Revisar `Litex/ws2812/` si el foco es display WS2812/DMA.
8. Revisar `migen_tutorial/DMA_cpu/Docs/` si el foco es DMA, UDP y SoC avanzado.
9. Revisar `Embedded/Buildroot-YuzukiSBC/README.md` solo si el objetivo es Linux embebido/Buildroot.

## Comandos utiles de inspeccion

```bash
git status --short --branch
git log --oneline --decorate --max-count=25
git diff --stat
git diff --name-status
find . -maxdepth 2 -type d | sort
rg --files -g 'Makefile'
rg --files -g 'README*'
```

## Pendientes sugeridos

- Decidir si los reportes locales `Litex/reporte_*.md` deben agregarse al repo.
- Revisar los cambios locales antes de cualquier nuevo pull/merge.
- Limpiar o ignorar caches y builds si no deben versionarse.
- Documentar en cada subproyecto que targets son los mantenidos actualmente.
- Normalizar rutas absolutas de herramientas externas en Makefiles o documentarlas por maquina.
- Separar, si se desea, Buildroot del material FPGA para reducir ruido de busqueda e historial.
