# Inventario del repositorio para WS2812/LiteX

Fecha local: 2026-07-10
Repositorio: `/home/andresrivera/digital_UN`
Rama de trabajo: `feat/ws2812-litex-final-project`

## Actualizacion de cierre

Archivos nuevos o relevantes de la ronda final:

```text
Litex/ws2812/ws2812_64led_check_TB.v
docs/ws2812/DMA_STREAM.md
docs/ws2812/log_sim_lattice_csr_64led_posedge_mem_retry.txt
docs/ws2812/log_sim_lattice_dma_64led_two_frames_posedge_mem.txt
docs/ws2812/log_build_i5_dma_integrated_ram_64led_60mhz_posedge_mem.txt
```

El cierre tecnico actual usa 64 LEDs. Los archivos generados en `Litex/build/**`, `.init`, `.vvp`, `.vcd`, objetos y firmware compilado quedan fuera de versionamiento mediante `.gitignore`.

La plataforma local sigue siendo `Litex/board/colorlight_i5.py`. La placa final solicitada, Colorlight 5A-75B, requiere confirmar revision fisica y adaptar plataforma/pines antes de programar.

## Conclusion de inventario

La implementacion WS2812 principal para el proyecto actual esta en `Litex/ws2812/` e integrada desde los SoC `Litex/colorlight_i5.py`, `Litex/colorlight_i5_no_bios.py` y, especialmente, `Litex/colorlight_i5_no_bios_dma.py`.

El flujo mas reciente del profesor parece ser:

```text
Litex/Makefile
  -> target sim_lattice_dma
  -> Litex/colorlight_i5_no_bios_dma.py
  -> Litex/NO_bios_fw_dma/
  -> Litex/ws2812/ws2812_streamer.py
  -> Litex/ws2812/ws2812_periph.v
  -> Litex/ws2812/led_mem_dual.v
  -> Litex/colorlight_i5_dma_TB.v
  -> Litex/colorlight_i5_no_bios_dma_sim.gtkw
```

La ruta CSR directa tambien existe:

```text
Litex/colorlight_i5_no_bios.py
  -> Litex/NO_bios_fw/
  -> Litex/ws2812/ws2812.py
  -> CSR w_address/w_data/we_a/init/done
```

Pero los commits mas recientes agregaron y corrigieron el camino DMA/Stream, por lo que no debe eliminarse ni reemplazarse.

## Arbol relevante

```text
Litex/
  Makefile
  colorlight_i5.py
  colorlight_i5_no_bios.py
  colorlight_i5_no_bios_dma.py
  colorlight_i5_TB.v
  colorlight_i5_dma_TB.v
  colorlight_i5_dma_pc_TB.v
  colorlight_i5_dma_reader_TB.v
  colorlight_i5_no_bios_sim.gtkw
  colorlight_i5_no_bios_dma_sim.gtkw
  csr.csv
  board/
    colorlight_i5.py
  firmware/
    Makefile
    main.c
    helpers.c
    linker.ld
  NO_bios_fw/
    Makefile
    main.c
    linker.ld
  NO_bios_fw_dma/
    Makefile
    main.c
    linker.ld
  ws2812/
    Makefile
    ws2812.v
    ctrl_ws.v
    count_ws.v
    comp_ws.v
    mux_ws.v
    ws2812_led.v
    ctrl_wsled.v
    count_wsled.v
    lsr_wsled.v
    ws2812_led_array.v
    ctrl_ws_arr.v
    count_addr.v
    comp_ws_arr.v
    led_mem.v
    led_mem_dual.v
    ws2812_periph.v
    ws2812.py
    ws2812_streamer.py
    generate_ws2812_streamer_verilog.py
    ws2812_streamer_generated.v
    *_TB.v
    *.gtkw
```

Copias pedagogicas relacionadas, no principales para este proyecto:

```text
basic_circuits/test_peripherals/rtl/cores/test/ws2812/
femtoRV/basic/rtl/cores/ws2812/
```

## Plataforma y hardware

Archivo de plataforma real:

```text
Litex/board/colorlight_i5.py
```

Datos confirmados en la plataforma:

| Elemento | Valor encontrado |
| --- | --- |
| Placa principal | Colorlight i5 |
| Revision i5 | `7.0` |
| FPGA i5 | `LFE5U-25F-6BG381C` |
| Placa alternativa | Colorlight i9 |
| Revision i9 | `7.2` |
| FPGA i9 | `LFE5U-45F-6BG381C` |
| Reloj externo | `clk25` en pin `P3` |
| Reset CPU | `cpu_reset_n` en pin `K18` |
| LED de usuario i5 | `user_led_n` en pin `U16` |
| Salida matriz | recurso `led_matrix`, subsenal `dout`, pin `G5` |
| Toolchain plataforma | `trellis` por defecto |

La CRG de los SoC usa entrada de 25 MHz y genera `sys_clk_freq`, que por defecto es `60e6` en los scripts Colorlight.

## Implementacion WS2812 actual

### Nivel 1: temporizador/protocolo de bit

Archivos:

```text
Litex/ws2812/ws2812.v
Litex/ws2812/ctrl_ws.v
Litex/ws2812/count_ws.v
Litex/ws2812/comp_ws.v
Litex/ws2812/mux_ws.v
```

Valores actuales:

```verilog
parameter fcia = 25000000;
parameter T0H = 11'd10;
parameter T1H = 11'd20;
parameter PER = 11'd31;
parameter RES = 11'd1250;
```

Estos valores corresponden al reloj de 25 MHz, no al `sys_clk_freq` de 60 MHz que los SoC declaran por defecto. Es un punto tecnico a revisar en fases de requisitos/timing.

### Nivel 2: transmision de un LED

Archivos:

```text
Litex/ws2812/ws2812_led.v
Litex/ws2812/ctrl_wsled.v
Litex/ws2812/count_wsled.v
Litex/ws2812/lsr_wsled.v
```

Responsabilidad: cargar palabra de 24 bits, transmitir MSB-first y reportar `done`.

### Nivel 3: transmision de matriz/framebuffer

Archivos:

```text
Litex/ws2812/ws2812_led_array.v
Litex/ws2812/ws2812_periph.v
Litex/ws2812/ctrl_ws_arr.v
Litex/ws2812/count_addr.v
Litex/ws2812/comp_ws_arr.v
Litex/ws2812/led_mem.v
Litex/ws2812/led_mem_dual.v
```

`ws2812_periph.v` usa `led_mem_dual.v` con puerto de escritura para CPU/loader y puerto de lectura para el controlador. Por defecto usa `SIZE=8`, equivalente a 256 posiciones.

## Framebuffer actual

Archivo:

```text
Litex/ws2812/led_mem_dual.v
```

Interfaz:

```text
clk
address -> data_r
we_a
w_address
w_data
```

Memoria:

```verilog
reg [23:0] MEM [0: (2**(addr_lenght) - 1)];
```

Inicializacion:

```verilog
$readmemh("./display.hex", MEM);
```

Esto depende del directorio de ejecucion de `vvp`; debe tratarse con cuidado porque las instrucciones piden evitar cwd ambiguo.

Politica de concurrencia actual: las escrituras por `we_a` se permiten mientras el controlador lee por el otro puerto. No hay bloqueo durante transmision.

## Wrappers LiteX/Migen

### CSR directo

Archivo:

```text
Litex/ws2812/ws2812.py
```

CSR:

```text
init
rst_cmd
w_data
w_address
we_a
done
```

Este wrapper instancia `ws2812_periph` y conecta directamente CSR a `w_data`, `w_address`, `we_a`, `init` y `rst_cmd`.

### Stream/DMA

Archivo:

```text
Litex/ws2812/ws2812_streamer.py
```

CSR propios:

```text
disp0_init
disp0_rst_cmd
disp0_done
disp0_loader_start
disp0_loader_done
disp0_loader_busy
```

Ademas, `colorlight_i5_no_bios_dma.py` agrega `disp0_dma` como `WishboneDMAReader`, con CSR de DMA generados por LiteX.

Funcionamiento:

1. Firmware llena un buffer en memoria.
2. Firmware configura `disp0_dma`.
3. Firmware escribe `disp0_loader_start`.
4. `WishboneDMAReader` emite palabras de 32 bits.
5. `WS2812StreamLoader` acepta stream, reordena bytes y escribe `w_data/w_address/we`.
6. Firmware inicia envio WS2812 con `disp0_init`.

## Firmware existente

### `Litex/NO_bios_fw/main.c`

Firmware no-BIOS base. Prueba multiplicador y luego escribe 64 posiciones del framebuffer mediante CSR directos:

```c
disp0_w_address_write(a);
disp0_w_data_write(a+b);
disp0_we_a_write(1);
disp0_we_a_write(0);
disp0_init_write(1);
disp0_init_write(0);
while(disp0_done_read() == 0){}
```

Aunque el periferico RTL por defecto tiene 256 posiciones, este firmware escribe solo 64.

### `Litex/NO_bios_fw_dma/main.c`

Firmware no-BIOS DMA reciente. Declara:

```c
#define WS2812_HW_LEDS 256
#define TEST_WORDS     256
```

Llena un buffer y carga el framebuffer mediante `disp0_dma` + loader:

```c
disp0_loader_start_write(1);
disp0_dma_base_write((uint32_t)ws2812_buffer);
disp0_dma_length_write(WS2812_HW_LEDS * 4);
disp0_dma_enable_write(1);
while (disp0_loader_done_read() == 0) {}
while (disp0_dma_done_read() == 0) {}
disp0_init_write(1);
disp0_init_write(0);
while (disp0_done_read() == 0) {}
```

Este confirma que el flujo reciente del profesor usa 256 LEDs y DMA/Stream.

### `Litex/firmware/main.c`

Firmware con BIOS/carga por `litex_term`. Actualmente tiene cambios locales preexistentes y esta enfocado en calculadora/multiplicador, no en WS2812.

## SoC LiteX

### `Litex/colorlight_i5.py`

SoC con BIOS/hardware. Integra:

- VexRiscv.
- LED chaser.
- `mult0`.
- `disp0` usando `ws2812_streamer.WS2812`.
- `disp0_dma` usando `WishboneDMAReader`.
- SPI flash.
- SDRAM.
- Ethernet opcional.

Nota: el archivo esta modificado localmente antes de esta tarea. Se observo duplicacion preexistente de `n_leds=256` y `with_usb_pll` en el diff local; no se modifico durante el inventario.

### `Litex/colorlight_i5_no_bios.py`

SoC no-BIOS base. Integra `mult0` y `disp0` con `ws2812.WS2812` CSR directo. Usa `NO_bios_fw/firmware.bin` si existe y deshabilita SDRAM en simulacion mediante `SIMULATION`.

### `Litex/colorlight_i5_no_bios_dma.py`

SoC no-BIOS DMA. Integra `uart_frame`, `mult0`, `disp0`, `disp0_dma`, SPI flash y deshabilita SDRAM en simulacion mediante `SIMULATION`. Usa `NO_bios_fw_dma/firmware.bin` si existe.

## Testbenches y GTKWave

Unitarios WS2812:

```text
Litex/ws2812/ws2812_TB.v
Litex/ws2812/ws2812_led_TB.v
Litex/ws2812/ws2812_led_array_TB.v
Litex/ws2812/ws2812_periph_TB.v
Litex/ws2812/led_mem_TB.v
Litex/ws2812/*_sim.gtkw
```

SoC:

```text
Litex/colorlight_i5_TB.v
Litex/colorlight_i5_dma_TB.v
Litex/colorlight_i5_dma_pc_TB.v
Litex/colorlight_i5_dma_reader_TB.v
Litex/colorlight_i5_no_bios_sim.gtkw
Litex/colorlight_i5_no_bios_dma_sim.gtkw
Litex/colorlight_i5_dma.gtkw
```

`colorlight_i5_dma_TB.v` contiene instrumentacion extensa para:

- PC del CPU.
- bus DMA.
- stream hacia loader.
- `disp0_w_address`.
- `disp0_w_data`.
- `disp0_we`.
- `disp0_busy`.
- `disp0_done`.
- memoria interna `ws2812_periph.mem0.MEM[idx]`.

## Makefiles y targets

### `Litex/Makefile`

Targets relevantes:

```text
fw_no_bios
sim_lattice
sim_lattice_dma
sim_efinix
svg
litex_term
clean
```

`sim_lattice_dma` es el target principal para la simulacion SoC WS2812 actual. En esta continuacion se ejecuto con el Python de `.venv-litex`, `WAVE=0`, `VCD=0`, `FINISH_ON_WS_DONE=1` y `SIM_N_LEDS=4` para obtener cierre funcional sin esperar la transmision RTL completa de 256 LEDs.

### `Litex/ws2812/Makefile`

Targets relevantes:

```text
sim
streamer_v
sim_streamer
sim_streamer_view
sim_post_syn
svg
configure_lattice
clean
```

## CSR y mapas actuales

`Litex/csr.csv` fue regenerado por el flujo LiteX del SoC `colorlight_i5` con WS2812 DMA. Los CSR relevantes confirmados son:

- `disp0`: base `0xf0001000`, con `init`, `rst_cmd`, `done`, `loader_start`, `loader_done` y `loader_busy`.
- `disp0_dma`: base `0xf0001800`, con `base`, `length`, `enable`, `done`, `loop` y `offset`.

Tambien se regeneraron headers y mapas bajo `Litex/build/colorlight_i5/software/include/generated/`. Las regiones relevantes son `rom=0x00000000` (`0x10000`), `sram=0x10000000` (`0x2000`), `main_ram=0x40000000` (`0x2000`), `spiflash=0x00200000` (`0x200000`) y `csr=0xf0000000` (`0x10000`).

## Archivos fuente

Se consideran fuente para este proyecto:

- `Litex/Makefile`
- `Litex/colorlight_i5.py`
- `Litex/colorlight_i5_no_bios.py`
- `Litex/colorlight_i5_no_bios_dma.py`
- `Litex/board/colorlight_i5.py`
- `Litex/ws2812/*.v`
- `Litex/ws2812/ws2812.py`
- `Litex/ws2812/ws2812_streamer.py`
- `Litex/NO_bios_fw/*.c`, `*.h`, `Makefile`, `linker.ld`
- `Litex/NO_bios_fw_dma/*.c`, `*.h`, `Makefile`, `linker.ld`
- `Litex/firmware/*.c`, `*.h`, `Makefile`, `linker.ld`
- `Litex/*_TB.v`
- `Litex/*.gtkw`

## Archivos generados o artefactos

No deben editarse manualmente como solucion permanente:

- `Litex/build/**`
- `Litex/colorlight_i5_rom.init`
- `Litex/colorlight_i5_sram.init`
- `Litex/colorlight_i5_mem.init`
- `Litex/colorlight_i5_synth.v`
- `Litex/ws2812/*.json`
- `Litex/ws2812/*_synth.v`
- `Litex/ws2812/*.bit`
- `Litex/ws2812/*.svf`
- `Litex/**/*.vcd`
- `Litex/**/*.vpp`
- `Litex/**/*.o`
- `Litex/**/*.d`
- `Litex/**/*.elf`
- `Litex/**/*.bin`
- `Litex/**/__pycache__/**`

## Archivos que si se podrian modificar

Solo si una fase posterior demuestra necesidad tecnica:

- `Litex/ws2812/ws2812.v`
- `Litex/ws2812/ctrl_ws.v`
- `Litex/ws2812/ws2812_led.v`
- `Litex/ws2812/ctrl_wsled.v`
- `Litex/ws2812/ws2812_periph.v`
- `Litex/ws2812/led_mem_dual.v`
- `Litex/ws2812/ws2812.py`
- `Litex/ws2812/ws2812_streamer.py`
- `Litex/NO_bios_fw_dma/main.c`
- `Litex/NO_bios_fw/main.c`
- `Litex/Makefile`
- testbenches WS2812/SoC y `.gtkw`

## Archivos que no se modificaran salvo bloqueo real

- `Litex/VexRiscv.v`
- `Litex/mult/**`
- `femtoRV/**`
- `basic_circuits/**`
- `Litex/Led_panel_12bpp/**`
- `Embedded/**`
- archivos generados en `Litex/build/**`

## Riesgos tecnicos encontrados

1. El temporizador WS2812 ya fue recalculado para `sys_clk_freq=60e6`: bit 0 alto 24 ciclos, bit 1 alto 48 ciclos, periodo de bit 75 ciclos y reset minimo 3000 ciclos.
2. La simulacion SoC DMA confirma que el loader escribe 256 palabras desde DMA. La transmision WS2812 completa de 256 LEDs sigue siendo costosa en RTL, por lo que el cierre automatico usa `SIM_N_LEDS=4`; el testbench mantiene el valor por defecto para comportamiento completo cuando no se sobrescribe.
3. `led_mem_dual.v` inicializa la memoria a cero y solo carga `display.hex` en simulacion con guardas `ifndef SYNTHESIS`, evitando fallos de sintesis por `$fopen`.
4. `ctrl_ws.v` y otros controladores usan asignaciones bloqueantes `=` en logica secuencial o asignaciones no bloqueantes en combinacional. Funcionan posiblemente en simulacion, pero no cumplen completamente las buenas practicas exigidas.
5. El build SoC con SDRAM externa no cierra por uso de BRAM (`DP16KD 60/56`). El build con `--integrated-main-ram-size=0x2000` genera bitstream, pero nextpnr reporta frecuencia maxima `57.14 MHz` para un objetivo de `60.00 MHz`.
6. La deteccion USB ve un FT232R (`0403:6001`), pero `openFPGALoader --detect` no encuentra una interfaz JTAG programable por defecto. No se debe programar FPGA hasta confirmar cable, placa y alimentacion.
7. `Litex/colorlight_i5.py` y otros archivos tenian cambios locales preexistentes; se preservan y no se revierten.
