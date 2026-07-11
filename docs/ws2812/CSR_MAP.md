# Mapa CSR WS2812

Fecha local: 2026-07-10
Fuente: `Litex/build/colorlight_i5/software/include/generated/csr.h` y `Litex/build/colorlight_i5/csr.csv`.

## Actualizacion 2026-07-11 - CSR Colorlight 5A-75B

El target `colorlight_5a_75b_ws2812_dma.py` genero un mapa CSR propio en:

```text
Litex/build/colorlight_5a_75b_ws2812/csr.csv
Litex/build/colorlight_5a_75b_ws2812/software/include/generated/csr.h
```

Bases CSR relevantes:

| Bloque | Base |
| --- | ---: |
| `mult0` | `0xf0000000` |
| `disp0` | `0xf0000800` |
| `disp0_dma` | `0xf0001000` |
| `ctrl` | `0xf0001800` |
| `identifier_mem` | `0xf0002000` |
| `timer0` | `0xf0002800` |
| `uart` | `0xf0003000` |

Registros `disp0`:

| Registro | Direccion | Tamano | Acceso |
| --- | ---: | ---: | --- |
| `disp0_init` | `0xf0000800` | 1 | RW |
| `disp0_rst_cmd` | `0xf0000804` | 1 | RW |
| `disp0_done` | `0xf0000808` | 1 | RO |
| `disp0_loader_start` | `0xf000080c` | 1 | RW |
| `disp0_loader_done` | `0xf0000810` | 1 | RO |
| `disp0_loader_busy` | `0xf0000814` | 1 | RO |

Registros `disp0_dma`:

| Registro | Direccion | Tamano | Acceso |
| --- | ---: | ---: | --- |
| `disp0_dma_base` | `0xf0001000` | 2 | RW |
| `disp0_dma_length` | `0xf0001008` | 1 | RW |
| `disp0_dma_enable` | `0xf000100c` | 1 | RW |
| `disp0_dma_done` | `0xf0001010` | 1 | RO |
| `disp0_dma_loop` | `0xf0001014` | 1 | RW |
| `disp0_dma_offset` | `0xf0001018` | 1 | RO |

Memoria integrada generada:

| Region | Base | Tamano |
| --- | ---: | ---: |
| `rom` | `0x00000000` | 64 KiB |
| `sram` | `0x10000000` | 8 KiB |
| `main_ram` | `0x40000000` | 8 KiB |
| `csr` | `0xf0000000` | 64 KiB |

## Actualizacion de variantes

Hay dos mapas CSR validos segun el target generado:

| Variante | SoC | Bloques WS2812 |
| --- | --- | --- |
| CSR directo | `colorlight_i5_no_bios.py` | `disp0` con `w_address`, `w_data`, `we_a`, `init`, `done` |
| DMA/Stream | `colorlight_i5_no_bios_dma.py` | `disp0` con loader + `disp0_dma` |

Los targets `sim_lattice` y `sim_lattice_dma` comparten y regeneran `Litex/build`, por lo que no deben ejecutarse en paralelo. La evidencia del cierre usa logs guardados, no una suposicion sobre el ultimo contenido de `Litex/build`.

Validacion CSR directa 64 LEDs:

```text
CSR->WS2812 write 64: addr=63 data=000049
CSR WS2812 DONE EDGE: ws_done_edges=1 csr_writes=64 max_addr=63 ws_addr=63 mem0=00000a mem63=000049
```

Validacion DMA 64 palabras/frame:

```text
LOADER DONE EDGE: ... writes=64 dma_len_words=64
WS2812 completed: observed DMA->WS2812 writes=128 loader_done_edges=2 ws_done_edges=2
```

## Estado

El mapa CSR fue regenerado con el flujo DMA/no-BIOS usando LiteX en `.venv-litex`. El archivo `Litex/csr.csv` en la raiz de `Litex/` sigue desactualizado y no debe usarse para cerrar WS2812; el mapa valido de esta corrida esta en `Litex/build/colorlight_i5/csr.csv`.

Comando que genero el mapa actual:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_i5_no_bios_dma.py --build --no-compile-software --integrated-main-ram-size=0x2000
```

## Bases CSR

| Bloque | Base |
| --- | ---: |
| `uart_frame` | `0xf0000000` |
| `mult0` | `0xf0000800` |
| `disp0` | `0xf0001000` |
| `disp0_dma` | `0xf0001800` |
| `ctrl` | `0xf0002000` |
| `identifier_mem` | `0xf0002800` |
| `leds` | `0xf0003000` |
| `spiflash` | `0xf0003800` |
| `timer0` | `0xf0004000` |
| `uart` | `0xf0004800` |

## Registros `disp0`

| Registro | Direccion | Tamano | Acceso | Funcion |
| --- | ---: | ---: | --- | --- |
| `disp0_init` | `0xf0001000` | 1 | RW | Inicia transmision WS2812 |
| `disp0_rst_cmd` | `0xf0001004` | 1 | RW | Fuerza envio de reset/latch en temporizador |
| `disp0_done` | `0xf0001008` | 1 | RO | Fin real de transmision del periferico |
| `disp0_loader_start` | `0xf000100c` | 1 | RW | Inicia carga de framebuffer desde stream/DMA |
| `disp0_loader_done` | `0xf0001010` | 1 | RO | Fin de carga del framebuffer |
| `disp0_loader_busy` | `0xf0001014` | 1 | RO | Loader ocupado |

## Registros `disp0_dma`

| Registro | Direccion | Tamano | Acceso | Funcion |
| --- | ---: | ---: | --- | --- |
| `disp0_dma_base` | `0xf0001800` | 2 | RW | Direccion base de lectura DMA, 64 bits |
| `disp0_dma_length` | `0xf0001808` | 1 | RW | Longitud DMA |
| `disp0_dma_enable` | `0xf000180c` | 1 | RW | Habilita transferencia |
| `disp0_dma_done` | `0xf0001810` | 1 | RO | Fin de DMA |
| `disp0_dma_loop` | `0xf0001814` | 1 | RW | Loop DMA |
| `disp0_dma_offset` | `0xf0001818` | 1 | RO | Offset actual |

## Nota importante sobre `done`

En simulacion se confirmo que:

- `disp0_loader_done` indica que el DMA/loader ya escribio el framebuffer.
- `disp0_done` indica que el periferico WS2812 termino de transmitir.

No son equivalentes. Los reportes y firmware deben distinguir ambos eventos.
