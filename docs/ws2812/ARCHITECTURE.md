# Arquitectura WS2812/LiteX

Fecha local: 2026-07-10
Base inspeccionada: `Litex/ws2812/`, `Litex/colorlight_i5*.py`, `Litex/Makefile`

## Actualizacion 2026-07-11 - Arquitectura Colorlight 5A-75B

Se agrego una variante fisica especifica para Colorlight 5A-75B:

```text
Litex/colorlight_5a_75b_ws2812_dma.py
```

Esta variante preserva el periferico WS2812 validado y cambia solamente la plataforma/constraints hacia `litex_boards.platforms.colorlight_5a_75b`. La arquitectura de producto es:

```mermaid
flowchart LR
    CPU[VexRiscv CPU] --> WB[Wishbone interconnect]
    WB --> ROM[ROM integrada 64 KiB]
    WB --> SRAM[SRAM integrada 8 KiB]
    WB --> MAIN[main_ram integrada 8 KiB]
    WB --> CSR[CSR bus]
    CSR --> MULT[mult0]
    CSR --> DISP[disp0 WS2812]
    CSR --> DMA[disp0_dma WishboneDMAReader]
    DMA --> STREAM[LiteX Stream 32-bit]
    STREAM --> LOADER[WS2812StreamLoader]
    LOADER --> FB[Framebuffer WS2812 64 LEDs]
    DISP --> PERIPH[ws2812_periph]
    PERIPH --> DOUT[ws2812.dout pin fisico pendiente]
```

El pin `j1:0` usado en el build 2026-07-11 es temporal para PnR. El diagrama final no debe fijar un pin de salida hasta confirmar el cableado DIN real de la matriz WS2812.

## Actualizacion de cierre

La arquitectura cerrada en esta ronda es de 64 LEDs. `ws2812_periph.v` usa `N_LEDS=64`, `ctrl_ws_arr.v` espera la lectura del framebuffer antes de iniciar cada LED y `led_mem_dual.v` entrega el puerto de lectura en flanco positivo. Con esto se evitan accesos a direccion 64. El build local i5 genera bitstream, pero la corrida fresca queda en `57.02 MHz (FAIL at 60.00 MHz)`, asi que el cierre temporal sigue pendiente.

La integracion fisica final para Colorlight 5A-75B sigue pendiente. El diagrama conserva `led_matrix.dout pin G5` porque ese dato proviene de la plataforma local `colorlight_i5`; no debe trasladarse a 5A-75B sin confirmar revision y pinout.

## Arquitectura general del SoC

```mermaid
flowchart LR
    CPU[VexRiscv CPU] --> WB[Wishbone interconnect]
    WB --> CSR[CSR bus]
    CSR --> MULT[mult0]
    CSR --> DISP[disp0 WS2812]
    CSR --> DMA[disp0_dma WishboneDMAReader]
    WB --> SRAM[SRAM]
    WB --> ROM[ROM]
    WB --> SPI[SPI Flash]
    WB --> SDRAM[SDRAM hardware flow]
    DMA --> STREAM[LiteX Stream]
    STREAM --> LOADER[WS2812StreamLoader]
    LOADER --> FB[Framebuffer dual-port]
    DISP --> DOUT[led_matrix.dout pin G5]
```

En simulacion no-BIOS DMA, `SIMULATION=1` evita agregar SDRAM y el firmware corre desde ROM integrada.

## Caja negra del periférico

```mermaid
flowchart LR
    CLK[clk sys] --> P[ws2812_periph]
    RST[reset sys] --> P
    INIT[init_m] --> P
    RSTCMD[rst_cmd] --> P
    WE[we_a] --> P
    WADDR[w_address 8b] --> P
    WDATA[w_data 24b] --> P
    P --> DONE[done]
    P --> DOUT[dout]
```

## Jerarquía de módulos

```mermaid
flowchart TB
    WS2812P[ws2812_periph] --> MEM[led_mem_dual]
    WS2812P --> ARRCTRL[ctrl_ws_arr]
    WS2812P --> ADDR[count_addr]
    WS2812P --> ADDRCMP[comp_ws_arr]
    WS2812P --> LED[ws2812_led]
    LED --> LSR[lsr_wsled]
    LED --> BITCNT[count_wsled]
    LED --> LEDCTRL[ctrl_wsled]
    LED --> TIMER[ws2812]
    TIMER --> TCTRL[ctrl_ws]
    TIMER --> TCNT[count_ws]
    TIMER --> TCMP[comp_ws]
    TIMER --> TMUX[mux_ws]
```

## Arquitectura interna del periférico

```mermaid
flowchart LR
    subgraph Write["Puerto escritura CPU/loader"]
        WADDR[w_address] --> MEM[led_mem_dual]
        WDATA[w_data] --> MEM
        WE[we_a] --> MEM
    end
    subgraph Read["Puerto lectura controlador"]
        ADDR[address] --> MEM
        MEM --> RGB[rgb 24b]
    end
    RGB --> LED[ws2812_led]
    ARR[ctrl_ws_arr] --> ADDRCTR[count_addr]
    ADDRCTR --> ADDR
    ADDR --> CMP[comp_ws_arr]
    CMP --> ARR
    LED --> ARR
    LED --> DOUT[dout]
```

## Separación control/camino de datos

### Camino de datos

| Bloque | Archivo | Funcion |
| --- | --- | --- |
| Registro de desplazamiento | `lsr_wsled.v` | Carga RGB/GRB y desplaza MSB-first |
| Contador de bits | `count_wsled.v` | Cuenta 24 bits por LED |
| Contador temporal | `count_ws.v` | Cuenta ciclos del bit/reset |
| Comparador temporal | `comp_ws.v` | Detecta fin de T0H/T1H/PER/RES |
| Mux de tiempos | `mux_ws.v` | Selecciona T0H, T1H, PER o RES |
| Contador direccion | `count_addr.v` | Recorre framebuffer |
| Comparador direccion | `comp_ws_arr.v` | Detecta fin de matriz |
| Framebuffer | `led_mem_dual.v` | Memoria `2**SIZE x 24` |
| Salida | `dout` | Señal serial WS2812 |

### Unidad de control

| FSM | Archivo | Estados |
| --- | --- | --- |
| Temporizador/bit | `ctrl_ws.v` | `START`, `CHK_SEL`, `SEND_RES`, `SEND_0`, `SEND_1`, `WAIT_TRST`, `WAIT_TH`, `SEND_PER`, `WAIT_T`, `END_SEND` |
| LED | `ctrl_wsled.v` | `START`, `CHK_SEL`, `SEND_BIT`, `WAIT_TX`, `SHIFT`, `CHECK_END`, `END_SEND` |
| Matriz | `ctrl_ws_arr.v` | `START`, `START_SEND`, `SEND_LED`, `WAIT_TX`, `INC`, `CHECK_END`, `END_SEND` |

## FSM temporizador

```mermaid
stateDiagram-v2
    [*] --> START
    START --> CHK_SEL: init_t
    START --> START: !init_t
    CHK_SEL --> SEND_0: sel=00
    CHK_SEL --> SEND_1: sel=01
    CHK_SEL --> SEND_RES: sel=10/11
    SEND_0 --> WAIT_TH: dout=1, sel_tim=T0H
    SEND_1 --> WAIT_TH: dout=1, sel_tim=T1H
    WAIT_TH --> SEND_PER: z
    WAIT_TH --> WAIT_TH: !z
    SEND_PER --> WAIT_T: dout=0, sel_tim=PER
    WAIT_T --> END_SEND: z
    WAIT_T --> WAIT_T: !z
    SEND_RES --> WAIT_TRST: dout=0, sel_tim=RES
    WAIT_TRST --> END_SEND: z
    WAIT_TRST --> WAIT_TRST: !z
    END_SEND --> START: done_t
```

## FSM transmisor de un LED

```mermaid
stateDiagram-v2
    [*] --> START
    START --> CHK_SEL: init
    START --> START: !init
    CHK_SEL --> SEND_BIT: init_t=1
    SEND_BIT --> WAIT_TX
    WAIT_TX --> SHIFT: done_t
    WAIT_TX --> WAIT_TX: !done_t
    SHIFT --> CHECK_END: shift, dec
    CHECK_END --> END_SEND: bit_count_zero
    CHECK_END --> CHK_SEL: !bit_count_zero
    END_SEND --> START: done_led
```

## FSM controlador de N LEDs

```mermaid
stateDiagram-v2
    [*] --> START
    START --> START_SEND: init_m
    START --> START: !init_m
    START_SEND --> SEND_LED: init_led=1
    SEND_LED --> WAIT_TX
    WAIT_TX --> INC: done_led
    WAIT_TX --> WAIT_TX: !done_led
    INC --> CHECK_END: inc_addr
    CHECK_END --> END_SEND: address_last
    CHECK_END --> START_SEND: !address_last
    END_SEND --> START: init_m
    END_SEND --> END_SEND: !init_m
```

## Secuencia CPU-CSR-WS2812-matriz

### Camino DMA principal

```mermaid
sequenceDiagram
    participant FW as Firmware C
    participant CSR as CSR disp0/disp0_dma
    participant DMA as WishboneDMAReader
    participant L as WS2812StreamLoader
    participant FB as led_mem_dual
    participant TX as ws2812_periph
    participant LED as Matriz WS2812

    FW->>CSR: disp0_loader_start=1
    FW->>CSR: dma_base, dma_length, dma_enable=1
    CSR->>DMA: configurar lectura Wishbone
    DMA->>L: stream data 32-bit
    L->>FB: we_a, w_address, w_data
    L->>CSR: loader_done=1
    FW->>CSR: disp0_init pulso
    CSR->>TX: init_m
    TX->>FB: leer address 0..N_LEDS-1
    TX->>LED: DOUT serial
    TX->>CSR: disp0_done=1
```

## Diagrama de flujo del algoritmo

```mermaid
flowchart TD
    A[Inicio firmware] --> B[Preparar framebuffer o buffer DMA]
    B --> C[Cargar pixel 0]
    C --> D{Quedan pixeles?}
    D -->|Si| E[Escribir siguiente palabra 24-bit]
    E --> F[Incrementar indice]
    F --> D
    D -->|No| G[Emitir pulso init]
    G --> H[Controlador lee address 0]
    H --> I[Transmitir 24 bits MSB-first]
    I --> J{Ultimo LED?}
    J -->|No| K[Incrementar direccion]
    K --> I
    J -->|Si| L[Emitir reset/latch]
    L --> M[done=1]
    M --> N[Firmware puede iniciar siguiente frame]
```

## Mapa de memoria

```mermaid
flowchart TB
    ROM["rom 0x00000000\nfirmware no-BIOS"]
    SPI["spiflash 0x00200000"]
    SRAM["sram 0x10000000\n.data .bss stack"]
    RAM["main_ram 0x40000000\nfirmware con BIOS"]
    CSR["csr 0xf0000000\nregistros perifericos"]
    CSR --> DISP["disp0 0xf0001000"]
    CSR --> DMA["disp0_dma 0xf0001800"]
    CSR --> UART[uart]
    CSR --> TIMER[timer0]
    CSR --> MULT[mult0]
```

## Mapa CSR

```mermaid
flowchart LR
    subgraph DISP["disp0"]
        INIT[init]
        RSTCMD[rst_cmd]
        DONE[done]
        LS[loader_start]
        LD[loader_done]
        LB[loader_busy]
        WD[w_data camino directo]
        WA[w_address camino directo]
        WE[we_a camino directo]
    end
    subgraph DMAREG["disp0_dma"]
        BASE[base]
        LEN[length]
        EN[enable]
        DDONE[done]
        LOOP[loop]
    end
    FW[Firmware C] --> DISP
    FW --> DMAREG
    DMAREG --> STREAM[WishboneDMAReader stream]
    STREAM --> DISP
```

## Flujo no-BIOS de simulación

```mermaid
flowchart TB
    A[Limpiar artefactos] --> B[Crear firmware.bin dummy]
    B --> C[Generar headers y regions.ld con LiteX]
    C --> D[Preparar picolibc local]
    D --> E[Compilar NO_bios_fw_dma]
    E --> F[Regenerar SoC con firmware real]
    F --> G[Copiar .init correctos]
    G --> H[Compilar testbench Icarus]
    H --> I[Ejecutar vvp]
    I --> J[Generar VCD]
    J --> K[Abrir GTKWave opcional]
```

## Flujo con BIOS

```mermaid
flowchart TB
    A[Generar SoC con BIOS] --> B[Sintesis/PnR/bitstream]
    B --> C[Programar FPGA]
    C --> D[Compilar firmware/firmware.bin]
    D --> E[litex_term --kernel firmware.bin]
    E --> F[Firmware corre en main_ram]
```

## Flujo de pruebas

```mermaid
flowchart LR
    A[Auditoria dependencias] --> B[Test timer autocheck]
    B --> C[Smoke test LED]
    C --> D[Smoke test periferico]
    D --> E[Test escritura streamer]
    E --> F[Sintesis unitaria]
    F --> G[Entorno LiteX en .venv-litex]
    G --> I[sim_lattice_dma reducido PASS]
    I --> J[CSR y headers regenerados]
    J --> K[Bitstream SoC con RAM integrada]
    K --> L{JTAG/board confirmado?}
    L -->|No| M[Validacion fisica bloqueada]
    L -->|Si| N[Programar y probar patrones]
```

## Observaciones tecnicas

- La jerarquia academica requerida ya existe.
- El camino DMA/Stream es una extension reciente y parece ser el flujo principal actual.
- El camino CSR directo existe y satisface el alcance base framebuffer + CSR, pero no es el camino de simulacion DMA reciente.
- La temporizacion WS2812 fue recalculada para `sys_clk_freq=60 MHz`: bit 0 alto 24 ciclos, bit 1 alto 48 ciclos, periodo de bit 75 ciclos y reset minimo 3000 ciclos.
- El riesgo de cierre principal ya no es funcional sino fisico/temporal: el build con SDRAM externa excede BRAM y el build con RAM integrada genera bitstream, pero reporta `57.14 MHz` maximos frente a los `60.00 MHz` requeridos.
- El testbench `ws2812_timer_check_TB.v` ya es autochecking para la temporizacion basica. El test SoC DMA reducido confirma carga DMA de 256 palabras y transmision WS2812 reducida mediante `SIM_N_LEDS=4`; la transmision completa de 256 LEDs queda lenta para simulacion RTL completa.
