# Reporte de temporizacion WS2812

Fecha local: 2026-07-10
Prueba: `make sim_ws2812_timer_check`

## Actualizacion 2026-07-11 - Timing Colorlight 5A-75B

El target nuevo `Litex/colorlight_5a_75b_ws2812_dma.py` cerro timing a 60 MHz en Colorlight 5A-75B revision asumida `7.0`:

```text
Max frequency for clock '$glbnet$crg_clkout0': 77.97 MHz (PASS at 60.00 MHz)
Critical path total: 12.83 ns
Slack setup aproximado: +3.84 ns
```

Comando ejecutado:

```bash
cd Litex
/home/andresrivera/digital_UN/.venv-litex/bin/python colorlight_5a_75b_ws2812_dma.py \
  --revision=7.0 \
  --ws2812-pin j1:0 \
  --build \
  --no-compile-software \
  --nextpnr-seed 1
```

Log:

```text
docs/ws2812/log_build_5a75b_ws2812_60mhz_seed1_j1_0_rerun.txt
```

La frecuencia del sistema no cambio, por lo que los parametros WS2812 simulados a 60 MHz siguen siendo los finales para esta variante: `T0H=24`, `T1H=48`, periodo de bit de 75 ciclos y reset/latch de 3000 ciclos minimo. No fue necesario repetir simulaciones por cambio de frecuencia.

## Actualizacion de cierre

El protocolo WS2812 y el cierre FPGA preliminar quedaron verificados para 64 LEDs:

```text
make sim_ws2812_full
PASS: 64 LEDs, 1536 bits/frame, GRB MSB-first, LED63, no LED64, second frame
```

El build i5 con RAM integrada mejoro el camino WS2812 al cambiar `led_mem_dual.v` para leer el framebuffer en flanco positivo, pero la corrida fresca no cerro a 60 MHz:

```text
Warning: Max frequency for clock '$glbnet$crg_clkout0': 57.02 MHz (FAIL at 60.00 MHz)
```

El camino critico anterior era una ruta de medio ciclo desde la RAM de framebuffer al shifter WS2812. La correccion elimina ese medio ciclo; el camino critico fresco queda fuera del bloque WS2812, en logica de CSR/DMA/SPI, pero todavia no alcanza 60 MHz.

## Cambio aplicado

El temporizador WS2812 ya no usa constantes heredadas de 25 MHz. Se ajusto para el dominio `sys` de LiteX a 60 MHz:

```verilog
parameter FCLK_HZ = 60000000;
parameter T0H = 16'd24;
parameter T1H = 16'd48;
parameter PER = 16'd73;
parameter RES = 16'd3000;
```

Tambien se ensancharon `count_ws`, `mux_ws` y `comp_ws` de 11 a 16 bits para soportar `RES=3000`.

## Resultado medido

```bash
cd Litex/ws2812
make sim_ws2812_timer_check
```

Salida:

```text
PASS: sel=0 high_cycles=24 total_cycles=75
PASS: sel=1 high_cycles=48 total_cycles=75
PASS: sel=2 high_cycles=0 total_cycles=3002
PASS: ws2812 timer protocol check completed
```

## Interpretacion

| Caso | Objetivo a 60 MHz | Medido | Estado |
| --- | ---: | ---: | --- |
| `0` alto | 24 ciclos / 0.40 us | 24 ciclos | PASS |
| `1` alto | 48 ciclos / 0.80 us | 48 ciclos | PASS |
| Periodo bit | 75 ciclos / 1.25 us | 75 ciclos | PASS |
| Reset/latch | >= 3000 ciclos / 50 us | 3002 ciclos | PASS |

`PER=73` es intencional porque la FSM mide `PER + 2` ciclos totales.

## Timing FPGA

El build SoC con RAM integrada produjo bitstream, pero nextpnr reporto:

```text
Warning: Max frequency for clock '$glbnet$crg_clkout0': 57.14 MHz (FAIL at 60.00 MHz)
```

Por tanto:

- Timing protocol WS2812 por ciclos RTL: PASS.
- Cierre FPGA a 60 MHz: FAIL/WARNING, requiere optimizacion o bajar `sys_clk_freq`.
