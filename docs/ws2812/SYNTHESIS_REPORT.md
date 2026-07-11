# Reporte de sintesis e implementacion WS2812

Fecha local: 2026-07-10

## Actualizacion de cierre

Se regenero el build con `N_LEDS=64` y lectura del framebuffer en flanco positivo. El build preliminar para la plataforma local `colorlight_i5` con RAM integrada genera bitstream, pero la corrida fresca no cierra timing a 60 MHz.

Comando:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

Log:

```text
docs/ws2812/log_build_i5_dma_integrated_ram_64led_60mhz_posedge_mem_final.txt
```

Resumen nextpnr:

```text
Warning: Max frequency for clock '$glbnet$crg_clkout0': 57.02 MHz (FAIL at 60.00 MHz)
Info: Program finished normally.
```

Recursos reportados:

| Recurso | Usado | Disponible | Porcentaje |
| --- | ---: | ---: | ---: |
| `TRELLIS_IO` | 12 | 197 | 6% |
| `DP16KD` | 48 | 56 | 85% |
| `MULT18X18D` | 4 | 28 | 14% |
| `EHXPLLL` | 1 | 2 | 50% |
| `USRMCLK` | 1 | 1 | 100% |
| `TRELLIS_FF` | 2891 | 24288 | 11% |
| `TRELLIS_COMB` | 5961 | 24288 | 24% |

Advertencia de alcance: este bitstream corresponde a `colorlight_i5` (`LFE5U-25F-6BG381C`) y no debe publicarse como bitstream final de Colorlight 5A-75B hasta confirmar la revision fisica, pinout y cierre temporal.

Los apartados historicos siguientes documentan la corrida anterior, donde el camino critico pasaba por una lectura de RAM en flanco negativo y no cerraba a 60 MHz.

## Resultado principal

Se genero bitstream del SoC DMA/no-BIOS con RAM integrada:

```text
Litex/build/colorlight_i5/gateware/colorlight_i5.bit
```

Comando:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

## Recursos con RAM integrada

nextpnr reporto:

| Recurso | Usado | Disponible | Porcentaje |
| --- | ---: | ---: | ---: |
| `TRELLIS_IO` | 12 | 197 | 6% |
| `DP16KD` | 48 | 56 | 85% |
| `MULT18X18D` | 4 | 28 | 14% |
| `EHXPLLL` | 1 | 2 | 50% |
| `USRMCLK` | 1 | 1 | 100% |
| `TRELLIS_FF` | 2953 | 24288 | 12% |
| `TRELLIS_COMB` | 5970 | 24288 | 24% |

Artefactos:

```text
colorlight_i5.bit     678 KiB
colorlight_i5.config  3.3 MiB
colorlight_i5.json    12 MiB
colorlight_i5.svf     1.4 MiB
```

## Timing

El build termino sin error de herramienta, pero no cerro timing a 60 MHz:

```text
Warning: Max frequency for clock '$glbnet$crg_clkout0': 57.14 MHz (FAIL at 60.00 MHz)
1 warning, 0 errors
Info: Program finished normally.
```

Estado: PASS de generacion de bitstream, FAIL/WARNING de cierre temporal a 60 MHz.

## Intento con SDRAM externa

Comando:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software
```

Resultado: Yosys pasa, pero nextpnr falla por recursos:

```text
DP16KD: 60/56 107%
ERROR: Unable to place cell 'ws2812_periph.mem0.MEM.0.0', no BELs remaining to implement cell type 'DP16KD'
```

Conclusion: para este SoC en `LFE5U-25F`, la variante con LiteDRAM SDRAM excede BRAM. La variante reproducible actual usa RAM integrada de 8 KiB.

## Correcciones necesarias para llegar al build

- `led_mem_dual.v`: separar `$fopen/$readmemh` de sintesis con `ifndef SYNTHESIS`.
- `colorlight_i5_no_bios_dma.py`: reemplazar pines invalidos `Y4/Y6` del UART auxiliar por pines validos `C17/B18`.

## Estado

| Punto | Estado |
| --- | --- |
| RTL sintetizable en SoC | PASS |
| Place and route con RAM integrada | PASS |
| Bitstream generado | PASS |
| Timing 60 MHz | FAIL/WARNING |
| SoC con SDRAM externa | FAIL recursos |
| Programacion FPGA | NO EJECUTADA |
