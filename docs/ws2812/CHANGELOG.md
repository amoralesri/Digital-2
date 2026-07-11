# Changelog WS2812

Fecha local: 2026-07-10
Rama de trabajo: `feat/ws2812-litex-final-project`

## Actualizacion 2026-07-11 - avance Colorlight 5A-75B

- Se confirmo JTAG con `openFPGALoader -c ft232RL --pins=TXD:CTS:DTR:RXD --detect`: `idcode 0x41111043`, Lattice ECP5 `LFE5U-25`.
- Se agrego `Litex/colorlight_5a_75b_ws2812_dma.py`, target minimo para Colorlight 5A-75B basado en `litex_boards.platforms.colorlight_5a_75b`.
- Se conservo la arquitectura WS2812/DMA de 64 LEDs y se uso ROM/RAM integrada como estrategia final tentativa.
- Se recompilo `NO_bios_fw_dma` contra `build/colorlight_5a_75b_ws2812`.
- Se genero bitstream 5A-75B con `--revision=7.0 --ws2812-pin j1:0 --nextpnr-seed 1`.
- El PnR post-route cerro timing a 60 MHz: `Fmax 77.97 MHz (PASS at 60.00 MHz)`, slack setup aproximado `+3.84 ns`.
- Se dejo programacion y validacion fisica en `BLOCKED`, porque `j1:0` es pin temporal y falta confirmar revision de PCB y pin DIN real de WS2812.

## Cierre 64 LEDs y bloqueo 5A-75B

- Se ajusto `ws2812_periph.v` para `N_LEDS=64` y comparacion contra `N_LEDS - 1`, evitando iniciar una direccion 64 inexistente.
- Se modifico `ctrl_ws_arr.v` para agregar espera de carga (`LOAD_WAIT`) antes de iniciar cada LED, incluyendo el primer LED y frames consecutivos.
- Se cambio el puerto de lectura de `led_mem_dual.v` a flanco positivo para eliminar el camino de medio ciclo entre framebuffer y shifter WS2812.
- Se actualizo `ws2812_streamer.py`, `colorlight_i5.py`, `colorlight_i5_no_bios_dma.py` y `NO_bios_fw_dma/main.c` para 64 LEDs.
- Se agrego `ws2812_64led_check_TB.v`, autochecking para 64 LEDs, 1536 bits por frame, GRB MSB-first, `LED63`, ausencia de `LED64` y segundo frame.
- Se agregaron targets `sim_ws2812_smoke` y `sim_ws2812_full`.
- Se extendieron `colorlight_i5_TB.v`, `colorlight_i5_dma_TB.v` y `Litex/Makefile` para cerrar simulaciones por `ws_done` y parametrizar cantidad de LEDs.
- Se verifico CSR directo con 64 escrituras y DMA con 64 palabras por frame, dos frames consecutivos.
- Se regenero el build i5 con RAM integrada; genera bitstream, pero la corrida fresca no cierra timing a 60 MHz: `57.02 MHz (FAIL at 60.00 MHz)`.
- Se documento que Colorlight 5A-75B sigue bloqueada por falta de revision, pinout, JTAG y confirmacion fisica. No se programo FPGA.
- Se agrego `.gitignore` para excluir artefactos generados de LiteX, simulacion y firmware.

Los apartados siguientes son historicos de la primera continuacion y quedan para trazabilidad.

## Continuacion de integracion y cierre

- Se creo el entorno `.venv-litex` con Migen, LiteX, LiteX-Boards, LiteDRAM, LiteEth, LiteSPI y dependencias `pythondata-*` necesarias para generar SoC y headers.
- Se corrigio el flujo `sim_lattice_dma` del `Makefile` principal para seleccionar Python, controlar VCD/GTKWave, limitar ciclos y cerrar la simulacion al observar `done` de WS2812.
- Se recalculo la temporizacion WS2812 para `60 MHz`: `T0H=24`, `T1H=48`, periodo de bit de 75 ciclos y reset minimo de 3000 ciclos.
- Se amplio el testbench DMA del SoC para instrumentar `loader_done`, `dma_done`, escrituras DMA, `ws_done` y cierre reducido con `SIM_N_LEDS=4`.
- Se compilo firmware no-BIOS y no-BIOS DMA con los headers regenerados por LiteX.
- Se regeneraron CSR y regiones de memoria reales: `disp0=0xf0001000`, `disp0_dma=0xf0001800`, `rom=0x00000000`, `sram=0x10000000`, `main_ram=0x40000000`, `csr=0xf0000000`.
- Se genero bitstream SoC con RAM integrada mediante `--integrated-main-ram-size=0x2000`. El build termina, pero nextpnr reporta timing insuficiente: `57.14 MHz` frente a `60.00 MHz`.
- Se intento el build SoC con SDRAM externa; no cierra por recursos BRAM (`DP16KD 60/56`).
- Se inspecciono hardware sin programar FPGA: `lsusb` y `openFPGALoader --scan-usb` detectan FT232R, pero `openFPGALoader --detect` no encuentra interfaz JTAG programable.
- Se actualizaron los reportes `DEPENDENCIES.md`, `CSR_MAP.md`, `MEMORY_AND_BOOT.md`, `TIMING_REPORT.md`, `TEST_REPORT.md`, `SYNTHESIS_REPORT.md`, `PHYSICAL_VALIDATION.md`, `FINAL_REPORT.md` y `README_WS2812.md` con los resultados actuales.

## Cambios realizados por esta intervencion

### Documentacion creada

- `docs/ws2812/BASELINE.md`: linea base de repositorio, rama, commit y estado inicial.
- `docs/ws2812/DEPENDENCIES.md`: auditoria de herramientas, Python, LiteX, RISC-V y FPGA.
- `docs/ws2812/REPOSITORY_MAP.md`: inventario de fuentes, flujos, firmware, testbenches y riesgos.
- `docs/ws2812/REQUIREMENTS.md`: requisitos verificables para WS2812, LiteX, firmware, simulacion y hardware.
- `docs/ws2812/ARCHITECTURE.md`: diagramas Mermaid de SoC, periferico, FSM, memoria, CSR y flujos.
- `docs/ws2812/CSR_MAP.md`: CSR confirmados en codigo y bloqueo de direcciones reales.
- `docs/ws2812/MEMORY_AND_BOOT.md`: regiones de memoria, BIOS, no-BIOS y linker.
- `docs/ws2812/TIMING_REPORT.md`: medicion de ciclos del temporizador WS2812 y riesgo 25 MHz vs 60 MHz.
- `docs/ws2812/TEST_REPORT.md`: matriz de pruebas ejecutadas, parciales y bloqueadas.
- `docs/ws2812/SYNTHESIS_REPORT.md`: sintesis/PnR/empaquetado unitario y bloqueo de SoC completo.
- `docs/ws2812/PHYSICAL_VALIDATION.md`: checklist fisico y estado bloqueado por falta de target programable confirmado.
- `docs/ws2812/FINAL_REPORT.md`: reporte final integral del proyecto.
- `README_WS2812.md`: guia de reproduccion para otra persona.

### Codigo de prueba creado

- `Litex/ws2812/ws2812_timer_check_TB.v`: testbench autochecking para medir bit 0, bit 1 y reset/latch del temporizador WS2812.

### Makefile modificado

- `Litex/ws2812/Makefile`: se agrego el target `sim_ws2812_timer_check` para compilar y ejecutar el testbench de temporizacion sin abrir GTKWave.

### Firmware modificado

- `Litex/NO_bios_fw_dma/main.c`: se reemplazo el ejemplo minimo por funciones reutilizables para cargar el framebuffer via DMA, iniciar `disp0`, esperar `done` con timeout y generar patrones de validacion de bajo brillo: apagado, rojo, verde, azul, blanco reducido, barrido, filas, columnas, ajedrezado y gradiente.

## Cambios funcionales no realizados

No se reescribio el RTL WS2812 existente. La auditoria encontro una implementacion jerarquica ya presente y funcional en simulacion unitaria.

No se modificaron:

- `Litex/VexRiscv.v`
- `Litex/mult/**`
- `femtoRV/**`
- `basic_circuits/**`
- `Litex/Led_panel_12bpp/**`
- archivos generados en `Litex/build/**`
- headers generados como `csr.h`, `soc.h` o `regions.ld`

## Cambios locales preexistentes preservados

Antes de esta intervencion ya estaban modificados:

- `Litex/board/colorlight_i5.py`
- `Litex/colorlight_i5.py`
- `Litex/csr.csv`
- `Litex/firmware/helpers.c`
- `Litex/firmware/main.c`

No se descartaron ni revirtieron.

## Artefactos generados por pruebas

Las simulaciones crearon VCD/VVP en `Litex/ws2812/`, por ejemplo:

- `ws2812_TB.vcd`
- `ws2812_led_TB.vcd`
- `ws2812_periph_TB.vcd`
- `ws2812_streamer_periph_TB.vcd`
- `ws2812_timer_check_TB.vvp`

La sintesis unitaria genero artefactos temporales en `/tmp`:

- `/tmp/ws2812_periph.json`
- `/tmp/ws2812_periph.config`
- `/tmp/ws2812_periph.bit`

## Pendiente tecnico

- Cerrar timing del bitstream a `60 MHz` o reducir formalmente la frecuencia objetivo.
- Decidir si se conserva el perfil con RAM integrada o se reduce uso de BRAM para recuperar SDRAM externa.
- Ejecutar una simulacion completa de 256 LEDs si se acepta el costo temporal, o mantener el cierre reducido `SIM_N_LEDS=4` como prueba de regresion rapida.
- Convertir mas pruebas LED/matriz a autocheck completo, no solo smoke/VCD.
- Confirmar cable JTAG, alimentacion, placa Colorlight i5 y matriz WS2812 antes de programar hardware.
- Validar fisicamente patrones de bajo brillo en Colorlight + matriz.
