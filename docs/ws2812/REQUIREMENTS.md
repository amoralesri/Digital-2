# Requisitos verificables del proyecto WS2812

Fecha local: 2026-07-10
Fuente de verdad: estado actual del repositorio `digital_UN`

## Actualizacion oficial de alcance

La instruccion de cierre actual pide orientar el proyecto a Colorlight 5A-75B. El repositorio local, sin embargo, contiene y construye una plataforma `colorlight_i5` local. Por tanto:

| Punto | Estado actual |
| --- | --- |
| Placa objetivo final | Colorlight 5A-75B |
| Revision 5A-75B | PENDIENTE de confirmacion fisica |
| FPGA/paquete 5A-75B | PENDIENTE de confirmacion fisica |
| Pin de salida WS2812 5A-75B | PENDIENTE de confirmacion fisica |
| Plataforma local verificable | `colorlight_i5`, `LFE5U-25F-6BG381C`, `led_matrix.dout=G5` |
| Cantidad de LEDs cerrada en RTL/SoC | 64 LEDs |

El requisito funcional cerrado en esta ronda es una matriz de 64 LEDs. Los textos historicos de 256 LEDs que aparecen mas abajo quedan como trazabilidad de la rama previa, pero ya no son el requisito principal del cierre.

## Alcance

Implementar, conservar o completar un periférico controlador WS2812 integrado en un SoC RISC-V LiteX para Colorlight i5/i9, con framebuffer, control desde firmware C, simulación RTL y flujo preparado para validación física.

El repositorio ya contiene una implementación parcial/funcional. Por tanto, el objetivo no es reescribir desde cero sino validar, corregir solo lo necesario y documentar el flujo reproducible.

## Plataforma objetivo

| Requisito | Valor |
| --- | --- |
| Placa principal | Colorlight i5 revision 7.0 |
| FPGA principal | Lattice ECP5 `LFE5U-25F-6BG381C` |
| Placa alternativa | Colorlight i9 revision 7.2 |
| FPGA alternativa | Lattice ECP5 `LFE5U-45F-6BG381C` |
| Reloj externo | 25 MHz (`clk25`) |
| Reloj de sistema SoC | 60 MHz por defecto en scripts Colorlight |
| Pin de datos matriz | `led_matrix.dout`, pin `G5` |
| Bus SoC | Wishbone |
| CPU | VexRiscv en LiteX |
| Nombre de periférico | `disp0` |

## Cantidad de LEDs

El firmware y wrapper DMA recientes usan:

```c
#define WS2812_HW_LEDS 256
```

y:

```python
ws2812_streamer.WS2812(..., n_leds=256)
```

Por tanto, el requisito principal actual es:

```text
N_LEDS = 256
```

La variante de 64 LEDs/8x8 no se adopta como requisito principal porque el repositorio actual indica 256 LEDs en el camino reciente del profesor. Si se necesita una matriz 8x8, debe parametrizarse/documentarse como variante futura o configuración alternativa.

## Protocolo WS2812

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-TIM-01 | Transmitir 24 bits por LED | Test RTL cuenta exactamente 24 ventanas de bit por LED |
| R-TIM-02 | Transmitir MSB-first | Test reconstruye bits desde `DOUT` y compara con palabra esperada |
| R-TIM-03 | Orden de color GRB o equivalente real | Documentar si `w_data` se interpreta como RGB o GRB y medir salida efectiva |
| R-TIM-04 | Bit 0 con tiempo alto correcto | Medir ciclos altos y comparar contra ciclos calculados para frecuencia real |
| R-TIM-05 | Bit 1 con tiempo alto correcto | Medir ciclos altos y comparar contra ciclos calculados para frecuencia real |
| R-TIM-06 | Periodo de bit correcto | Medir periodo total por bit |
| R-TIM-07 | Reset/latch final | Medir nivel bajo final >= 50 us equivalente |
| R-TIM-08 | Parametrizar frecuencia | No depender de valores de 25 MHz si el dominio real es 60 MHz |

Valores de referencia implementados para `ClockSignal("sys")` a 60 MHz:

```text
T0H = 24 ciclos
T1H = 48 ciclos
PER = 75 ciclos medidos por ventana completa
RES >= 3000 ciclos
```

Si se cambia `sys_clk_freq`, estos ciclos deben recalcularse y volver a validarse con `ws2812_timer_check_TB.v`.

## Arquitectura RTL

Debe conservarse la arquitectura jerárquica ya existente:

| Nivel | Módulos actuales | Requisito |
| --- | --- | --- |
| Bit/timer | `ws2812.v`, `ctrl_ws.v`, `count_ws.v`, `comp_ws.v`, `mux_ws.v` | Generar bit 0, bit 1 y reset/latch con `done_t` |
| LED | `ws2812_led.v`, `ctrl_wsled.v`, `count_wsled.v`, `lsr_wsled.v` | Enviar exactamente 24 bits MSB-first y generar `done_led` |
| Matriz | `ws2812_periph.v`, `ctrl_ws_arr.v`, `count_addr.v`, `comp_ws_arr.v`, `led_mem_dual.v` | Recorrer exactamente `N_LEDS` posiciones y generar `done` |

No se debe convertir el diseño en una FSM monolítica.

## Framebuffer

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-FB-01 | Memoria de `N_LEDS x 24 bits` | Instancia RTL tiene profundidad suficiente para `N_LEDS` |
| R-FB-02 | Una posición por LED | Test escribe/lee posiciones 0, 1, media y `N_LEDS-1` |
| R-FB-03 | Escritura por CPU/loader | `w_address`, `w_data`, `we_a` escriben contenido correcto |
| R-FB-04 | Lectura por controlador | La palabra transmitida coincide con memoria |
| R-FB-05 | Política durante `busy` | Documentar y probar que se permiten escrituras concurrentes por dual-port |
| R-FB-06 | Inicialización reproducible | Evitar dependencia ambigua de `./display.hex` o documentar cwd exacto |

Politica actual seleccionada:

```text
Se permiten escrituras durante transmisión porque `led_mem_dual.v` usa puerto de escritura y puerto de lectura separados. Esas escrituras pueden afectar el frame actual si se hacen antes de que la dirección correspondiente sea leída.
```

## CSR

### Camino CSR directo

CSR mínimos ya modelados por `Litex/ws2812/ws2812.py`:

| CSR | Requisito |
| --- | --- |
| `disp0_init` | Iniciar transmisión |
| `disp0_rst_cmd` | Solicitar reset/latch si el diseño lo usa |
| `disp0_w_data` | Escribir 24 bits útiles |
| `disp0_w_address` | Seleccionar posición del framebuffer |
| `disp0_we_a` | Pulso de escritura |
| `disp0_done` | Indicar fin real de transmisión |

### Camino DMA/Stream

CSR mínimos del camino principal reciente:

| CSR | Requisito |
| --- | --- |
| `disp0_init` | Iniciar salida WS2812 después de cargar framebuffer |
| `disp0_rst_cmd` | Control de reset/latch |
| `disp0_done` | Fin de transmisión de la matriz |
| `disp0_loader_start` | Iniciar carga del framebuffer desde stream |
| `disp0_loader_done` | Indicar fin de carga de `N_LEDS` palabras |
| `disp0_loader_busy` | Indicar loader activo |
| `disp0_dma_*` | Configurar y ejecutar `WishboneDMAReader` |

Requisitos CSR:

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-CSR-01 | `w_address`/loader cubre todas las posiciones | Test alcanza `0..N_LEDS-1` |
| R-CSR-02 | `w_data` conserva 24 bits | Test escribe patrones con bits altos/bajos |
| R-CSR-03 | `start/init` es inequívoco | Pulso inicia una sola transmisión |
| R-CSR-04 | `done` indica final real | `done` sube después del último LED y reset/latch |
| R-CSR-05 | `busy` activo durante carga DMA | En wrapper stream `loader_busy` activo mientras carga/draina |
| R-CSR-06 | Segundo frame | Se puede iniciar una segunda transmisión después de `done` |

No se editará manualmente `csr.h`; las direcciones reales deben salir de generación LiteX.

## Integración LiteX

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-SOC-01 | `disp0` instanciado en Colorlight | Aparece en script SoC y gateware generado |
| R-SOC-02 | Pin real conectado | `platform.request("led_matrix", 0)` usa pin `G5` |
| R-SOC-03 | Fuentes Verilog agregadas | `platform.add_source(...)` incluye todos los módulos necesarios |
| R-SOC-04 | CSR generados | `csr.csv` y `csr.h` contienen `disp0` |
| R-SOC-05 | No romper UART | Firmware con BIOS y no-BIOS conservan UART si aplica |
| R-SOC-06 | No romper `mult0` | Multiplicador no se modifica salvo dependencia real |
| R-SOC-07 | Simulación sin SDRAM | `SIMULATION=1` evita SDRAM en no-BIOS si ese flujo lo requiere |

## Firmware C

El firmware debe proporcionar o aproximar estas funciones:

```c
uint32_t ws2812_pack_grb(uint8_t r, uint8_t g, uint8_t b);
void ws2812_set_pixel(uint32_t index, uint8_t r, uint8_t g, uint8_t b);
void ws2812_set_pixel_grb(uint32_t index, uint32_t grb);
void ws2812_fill(uint8_t r, uint8_t g, uint8_t b);
void ws2812_clear(void);
bool ws2812_show(uint32_t timeout);
```

En el camino DMA, `set_pixel` puede llenar un buffer RAM y luego usar DMA para cargar el framebuffer del periférico. En el camino CSR directo, `set_pixel` puede escribir `disp0_w_address`, `disp0_w_data` y `disp0_we_a`.

Patrones mínimos:

| ID | Patrón | Criterio |
| --- | --- | --- |
| R-FW-01 | Apagado total | Todos los pixeles 0 |
| R-FW-02 | Rojo | Frame completo rojo con brillo seguro |
| R-FW-03 | Verde | Frame completo verde con brillo seguro |
| R-FW-04 | Azul | Frame completo azul con brillo seguro |
| R-FW-05 | Blanco reducido | No usar blanco máximo para validación física |
| R-FW-06 | Barrido LED por LED | Control individual visible |
| R-FW-07 | Filas | Confirmar mapeo lógico |
| R-FW-08 | Columnas | Confirmar mapeo lógico |
| R-FW-09 | Ajedrezado | Confirmar alternancia |
| R-FW-10 | Gradiente/incremental | Confirmar datos variables |
| R-FW-11 | Animación corta | Confirmar frames sucesivos |

## Simulación

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-SIM-01 | Test temporizador | Autocheck de bit 0, bit 1, periodo y reset |
| R-SIM-02 | Test LED | Autocheck de 24 bits MSB-first |
| R-SIM-03 | Test matriz | Autocheck de `N_LEDS` sin LED extra |
| R-SIM-04 | Test memoria | Escritura/lectura de framebuffer |
| R-SIM-05 | Simulación SoC | CPU escribe/carga framebuffer, inicia `disp0`, `done` sube |
| R-SIM-06 | VCD | Generar VCD reproducible |
| R-SIM-07 | GTKWave | `.gtkw` con señales clave sin rutas personales absolutas |

Una prueba solo se marca PASS si se ejecuta y termina sin error.

## Síntesis e implementación

| ID | Requisito | Criterio verificable |
| --- | --- | --- |
| R-SYN-01 | Sintetiza sin errores | Yosys termina OK |
| R-SYN-02 | Place-and-route | `nextpnr-ecp5` termina OK |
| R-SYN-03 | Bitstream | `ecppack` genera `.bit` |
| R-SYN-04 | Timing | Reportar frecuencia/slack |
| R-SYN-05 | Utilización | Reportar LUT/FF/BRAM/PLL |

Estas fases dependen de poder generar el gateware LiteX actual.

## Validación física

Solo puede marcarse PASS si se detecta placa/programador y se observa la matriz real.

Checklist:

- Alimentación externa suficiente.
- Tierra común FPGA/matriz.
- Corriente máxima calculada.
- No usar blanco a máximo brillo en los 256 LEDs.
- Verificar nivel lógico de datos.
- Considerar level shifter.
- Capacitor de alimentación.
- Resistencia serie en datos.
- Confirmar orden físico/serpentina antes de cambiar mapeo lógico.

## Criterios de aceptación

El proyecto se considera aceptado si cada punto queda como `PASS` o `BLOCKED` con causa demostrada:

- Hardware RTL: bit, LED, matriz, framebuffer, reset/latch y segunda actualización.
- LiteX: `disp0`, CSR, firmware y mapa real.
- Simulación: unitarias y SoC con VCD.
- Síntesis: bitstream y reportes.
- Físico: patrones observados, si hay hardware.
- Documentación: comandos, diagramas, limitaciones y resultados reales.
