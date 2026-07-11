# Memorias y arranque

Fecha local: 2026-07-10
Fuente: `regions.ld`, `csr.csv`, firmware ELF y build LiteX actual.

## Actualizacion 64 LEDs

El firmware DMA actual usa 64 LEDs:

```c
#define WS2812_HW_LEDS 64u
```

La transferencia DMA por frame es:

```text
64 palabras de 32 bits = 256 bytes
```

Evidencia de simulacion:

```text
LOADER DONE EDGE: ... writes=64 dma_off=64 dma_len_words=64
WS2812 DONE EDGE: ... ws_addr=3 ...
```

El build tree `Litex/build/**` es transitorio: cada target de simulacion puede eliminarlo y regenerarlo para la variante CSR directa o DMA. Los mapas generados deben interpretarse junto con el comando que los produjo.

## Regiones de memoria actuales

Mapa generado para el build DMA/no-BIOS con RAM integrada:

| Region | Base | Tamano |
| --- | ---: | ---: |
| `rom` | `0x00000000` | `0x00010000` / 64 KiB |
| `sram` | `0x10000000` | `0x00002000` / 8 KiB |
| `main_ram` | `0x40000000` | `0x00002000` / 8 KiB |
| `spiflash` | `0x00200000` | `0x00200000` / 2 MiB |
| `csr` | `0xf0000000` | `0x00010000` / 64 KiB |

Archivo fuente:

```text
Litex/build/colorlight_i5/software/include/generated/regions.ld
```

## Firmware no-BIOS DMA

Archivos:

```text
Litex/colorlight_i5_no_bios_dma.py
Litex/NO_bios_fw_dma/Makefile
Litex/NO_bios_fw_dma/linker.ld
Litex/NO_bios_fw_dma/main.c
```

El SoC fuerza:

```python
kwargs["integrated_rom_size"] = 0x10000
kwargs["cpu_reset_address"]   = 0x00000000
```

El firmware se compilo correctamente:

```text
Litex/NO_bios_fw_dma/firmware.elf
Litex/NO_bios_fw_dma/firmware.bin
Litex/NO_bios_fw_dma/firmware.lst
```

`readelf` reporto:

```text
Class: ELF32
Machine: RISC-V
Entry point address: 0x0
```

Uso de memoria reportado:

```text
ROM usage: 1.34 KiB (2.10%)
SRAM usage: 1.00 KiB (12.50%)
```

## Firmware no-BIOS base

Tambien compilo despues de actualizar Makefile/linker:

```text
Litex/NO_bios_fw/firmware.elf
Litex/NO_bios_fw/firmware.bin
Litex/NO_bios_fw/firmware.lst
```

Uso reportado:

```text
ROM usage: 3.30 KiB (5.15%)
SRAM usage: 0.02 KiB (0.29%)
```

## Build de gateware

El build que genero bitstream uso RAM integrada para evitar sobreuso de BRAM por LiteDRAM:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

Artefactos principales:

```text
Litex/build/colorlight_i5/gateware/colorlight_i5.bit
Litex/build/colorlight_i5/gateware/colorlight_i5.config
Litex/build/colorlight_i5/gateware/colorlight_i5.json
Litex/build/colorlight_i5/gateware/colorlight_i5.svf
```

## Advertencias

- Los archivos bajo `Litex/build/**`, `csr.h`, `regions.ld`, `.init`, `.json`, `.config` y `.bit` son generados.
- No deben editarse manualmente como solucion permanente.
- El build con SDRAM externa fallo por recursos: `DP16KD: 60/56`. El build con RAM integrada uso `DP16KD: 48/56`.
