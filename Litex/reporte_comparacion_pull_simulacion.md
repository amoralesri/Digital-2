# Reporte de comparacion del ultimo pull: correcciones de simulacion LiteX

Fecha: 2026-06-16  
Repositorio: `/home/andresrivera/digital_UN`  
Directorio principal revisado: `/home/andresrivera/digital_UN/Litex`

## 1. Rango comparado

Se comparo exactamente el estado anterior al ultimo pull contra el estado nuevo traido desde GitHub:

- Antes del pull: `fc7a3c9d`
- Despues del pull: `12c3e0ba`
- Rango Git usado: `fc7a3c9d..12c3e0ba`

El pull trajo 3 commits:

- `14b576ce fixing Litex`
- `c042cd2f Fixing no bios simulation`
- `12c3e0ba Fixing litex simulation`

## 2. Resumen general

El cambio principal fue convertir la simulacion no-BIOS en un flujo mas reproducible:

1. Se agregaron scripts/targets para construir firmware no-BIOS.
2. Se genera primero un `firmware.bin` dummy para romper la dependencia circular entre headers LiteX y firmware.
3. Se generan `regions.ld` y headers CSR.
4. Se compilan librerias de software LiteX.
5. Se compila el firmware no-BIOS real.
6. Se regenera el SoC embebiendo ese firmware en ROM.
7. Se copian los `.init` correctos al directorio donde la simulacion los lee.
8. Se agrego una vista GTKWave para verificar PC, multiplicador, UART, WS2812 y memoria del LED.

Segun el profesor, con estos cambios ya funcionan las simulaciones. La evidencia en el repo concuerda con esa intencion: ahora hay flujo dedicado para no-BIOS, testbench conectado a UART, ROM init reducida/actualizada, periferico `disp0` activo y archivo `.gtkw` con senales relevantes.

## 3. Archivos modificados o agregados

| Archivo | Tipo | Proposito probable |
| --- | --- | --- |
| `Litex/Makefile` | Nuevo | Agrega targets de build/simulacion, especialmente `sim_lattice` y `fw_no_bios`. |
| `Litex/simulate.sh` | Nuevo | Script paso a paso para construir y preparar simulacion no-BIOS. |
| `Litex/colorlight_i5_no_bios.py` | Modificado | Ajusta SoC no-BIOS: ROM mas grande, WS2812 habilitado, SDRAM omitida en simulacion. |
| `Litex/NO_bios_fw/Makefile` | Modificado | Simplifica objetos del firmware no-BIOS. |
| `Litex/NO_bios_fw/main.c` | Modificado | Cambia prueba: usa multiplicador y luego escribe memoria del periferico LED/WS2812. |
| `Litex/colorlight_i5_TB.v` | Modificado | Conecta UART, aumenta tiempo de simulacion y dumpea memoria del LED. |
| `Litex/colorlight_i5_no_bios_sim.gtkw` | Nuevo | Configuracion GTKWave para ver PC, multiplicador, WS2812 y memoria LED. |
| `Litex/colorlight_i5_rom.init` | Modificado | ROM init actualizada para el firmware no-BIOS nuevo. |
| `Litex/colorlight_i5_mem.init` | Modificado | Identificador LiteX actualizado. |
| `Litex/colorlight_daniel.py` | Nuevo | Otro SoC/plataforma de referencia con panel LED 12bpp/RMII; no parece ser el flujo principal de esta simulacion. |
| `Litex/load.py` | Nuevo | Script de programacion externo para Efinix; no es central para la simulacion no-BIOS. |

## 4. Cambios cuantitativos

Resumen `git diff --stat`:

```text
11 files changed, 711 insertions(+), 1271 deletions(-)
```

Por archivo:

```text
Litex/Makefile                       | 171 +++++
Litex/NO_bios_fw/Makefile            |   2 +-
Litex/NO_bios_fw/main.c              |  29 +-
Litex/colorlight_daniel.py           | 250 +++++++
Litex/colorlight_i5_TB.v             |  17 +-
Litex/colorlight_i5_mem.init         |  10 +-
Litex/colorlight_i5_no_bios.py       |  25 +-
Litex/colorlight_i5_no_bios_sim.gtkw |  79 ++
Litex/colorlight_i5_rom.init         | 1315 ++--------------------------------
Litex/load.py                        |   5 +
Litex/simulate.sh                    |  79 ++
```

Archivos finales relevantes:

- `Litex/colorlight_i5_rom.init`: 214 lineas.
- `Litex/colorlight_i5_mem.init`: 47 lineas.
- `Litex/colorlight_i5_no_bios_sim.gtkw`: 79 lineas.
- `Litex/Makefile`: 171 lineas.
- `Litex/simulate.sh`: 78 lineas.

## 5. Cambios en el flujo de build/simulacion

### Nuevo `Litex/Makefile`

Se agrego un Makefile principal en `Litex/`.

Partes importantes:

- Define `TARGET=colorlight_i5`.
- Usa `SOC_SCRIPT="colorlight_i5_no_bios.py"`.
- Usa `FW_NB_DIR = NO_bios_fw`.
- Usa `BUILD_DIR="build/colorlight_i5"`.
- Usa `ROM_SIZE=65536`.

El target mas importante es `sim_lattice`, que hace:

1. Limpia `build`, VCDs, VPPs y firmware no-BIOS previo.
2. Crea `NO_bios_fw/firmware.bin` dummy.
3. Genera headers CSR y `regions.ld`.
4. Compila librerias de software.
5. Compila el firmware real.
6. Regenera el SoC con `SIMULATION=1`.
7. Copia `colorlight_i5_rom.init` y `colorlight_i5_sram.init` desde `build/colorlight_i5/gateware/` hacia `Litex/`.
8. Compila simulacion RTL con `iverilog`.
9. Ejecuta `vvp`.
10. Abre `gtkwave`.

Esto ataca directamente el problema detectado antes: el testbench leia `.init` por ruta relativa y podia tomar archivos viejos o equivocados.

### Nuevo `Litex/simulate.sh`

El script `simulate.sh` implementa la misma idea, pero mas explicita y con verificaciones:

1. Crea firmware dummy.
2. Genera `regions.ld` y headers.
3. Compila librerias LiteX.
4. Verifica que exista `picolibc.h`.
5. Compila firmware real.
6. Reporta tamanos de secciones.
7. Verifica que el firmware quepa en ROM.
8. Regenera SoC embebiendo firmware.
9. Copia `.init` al directorio actual.

Nota: en el script, la llamada final a `make sim_lattice` esta comentada. Es decir, el script prepara el entorno y los `.init`, pero no lanza toda la simulacion por si solo a menos que se descomente o se corra `make sim_lattice`.

## 6. Cambios en `colorlight_i5_no_bios.py`

Este archivo recibio cambios muy importantes:

### 6.1 ROM mas grande

Antes:

```python
kwargs["integrated_rom_size"] = 0x8000
```

Ahora:

```python
kwargs["integrated_rom_size"] = 0x10000
```

Proposito: dar mas espacio al firmware no-BIOS embebido en ROM. Esto reduce el riesgo de que el firmware no quepa.

### 6.2 WS2812 habilitado

Antes estaba comentado:

```python
#from ws2812 import ws2812
#SoCCore.add_csr(self,"disp0")
#self.submodules.disp0 = ws2812.WS2812(...)
```

Ahora esta activo:

```python
from ws2812 import ws2812
SoCCore.add_csr(self,"disp0")
self.submodules.disp0 = ws2812.WS2812(platform, platform.request("led_matrix",0))
```

Proposito: permitir que el firmware escriba a `disp0_*` y que en simulacion se observe como cambia la memoria del LED.

### 6.3 SDRAM deshabilitada en simulacion

Ahora la SDRAM solo se agrega si no esta activa la variable de entorno `SIMULATION`:

```python
if not os.environ.get('SIMULATION'):
    self.add_sdram(...)
```

Proposito: simplificar la simulacion no-BIOS. Si el firmware corre desde ROM interna y usa SRAM/CSR, no necesita inicializar ni simular SDRAM completa.

## 7. Cambios en firmware no-BIOS

### `NO_bios_fw/Makefile`

Antes compilaba:

```make
OBJECTS= crt0.o isr.o helpers.o main.o uart.o
```

Ahora compila:

```make
OBJECTS= crt0.o isr.o main.o uart.o
```

Proposito probable: reducir dependencias/tamano del firmware no-BIOS y evitar compilar `helpers.c` si no se usa.

### `NO_bios_fw/main.c`

El firmware cambio de una prueba simple del multiplicador a una prueba combinada multiplicador + LED/WS2812.

Antes:

```c
mult0__A_write(0x10);
mult0__B_write(0x20);
mult0_init_write(1);
mult0_init_write(0);
while(mult0_done_read() == 0);
c = mult0_pp_read();
printf("A = %d, B = %d, A*B = %d\n\n", a, b, c);
```

Ahora:

```c
mult0__A_write(122);
mult0__B_write(122);
mult0_init_write(1);
mult0_init_write(1);
mult0_init_write(0);
while(mult0_done_read() == 0){}
c = mult0_pp_read();

for(a=0; a < 64; a++){
    disp0_w_data_write(a+b);
    disp0_w_address_write(a);
}
disp0_init_write(1);
disp0_init_write(0);
while(disp0_done_read() == 0){}
b = b + 64;
```

Proposito:

- Probar que el CPU arranca en no-BIOS.
- Probar escritura CSR al multiplicador.
- Probar `done` del multiplicador.
- Probar escritura CSR al periferico `disp0`.
- Ver en GTKWave que la memoria interna del LED cambia.

El valor `b` empieza en 10 y luego sube de 64 en 64, asi que en cada iteracion el patron escrito al buffer LED cambia.

## 8. Cambios en el testbench

Archivo: `Litex/colorlight_i5_TB.v`

Cambios importantes:

### 8.1 Timescale

Antes:

```verilog
`timescale 1us / 1ns
```

Ahora:

```verilog
`timescale 1ns / 1ps
```

Proposito: dar una base temporal mas fina para simular UART/clock/SoC y para que GTKWave sea mas consistente con señales rapidas.

### 8.2 UART conectada

Antes el testbench no conectaba `serial_tx` ni `serial_rx` al DUT.

Ahora:

```verilog
wire TXD;

colorlight_i5 uut(
    .clk25(CLK),
    .cpu_reset_n(!RESET),
    .serial_tx(TXD),
    .serial_rx(RXD)
);
```

Proposito: permitir observar salida serial y evitar puertos UART flotantes en la simulacion.

### 8.3 Dump de memoria LED

Se agrego:

```verilog
for(idx = 0; idx < 63; idx = idx +1)
    $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.mem0.MEM[idx]);
```

Proposito: registrar en el VCD las posiciones de memoria interna del periferico WS2812/LED. Esto coincide con lo que dijo el profesor: en `colorlight_i5_no_bios_sim.gtkw` se puede ver como cambia la memoria del LED.

### 8.4 Mas tiempo de simulacion

Antes:

```verilog
#(tck*50000) $finish;
```

Ahora:

```verilog
#(tck*100000) $finish;
```

Proposito: darle mas tiempo al CPU para arrancar, ejecutar firmware, escribir CSR, esperar `done` y actualizar memoria LED.

## 9. Archivo GTKWave nuevo

Archivo: `Litex/colorlight_i5_no_bios_sim.gtkw`

Este archivo abre el VCD:

```text
/Work/Embedded/digital_UN/Litex/colorlight_i5_TB.vcd
```

Senales incluidas:

- PC del VexRiscv:
  - `colorlight_i5_TB.uut.VexRiscv.decode_PC[31:0]`
- Reset/clock/UART:
  - `serial_tx`
  - `serial_rx`
  - `sys_clk`
  - `cpu_reset_n`
  - `sys_rst`
- Multiplicador:
  - `mult_32.A[15:0]`
  - `mult_32.B[15:0]`
  - `mult_32.init`
  - `mult_32.w_add`
  - `mult_32.w_sh`
  - `mult_32.done`
  - `mult_32.control0.state[2:0]`
  - `mult_32.pp[31:0]`
- WS2812/LED:
  - `led_matrix0_dout`
  - `ws2812_periph.dout`
  - `ws2812_periph.ctrl0.state[2:0]`
  - `ws2812_periph.done_led`
  - `ws2812_periph.ctrl0.init_m`
  - `ws2812_periph.done`
- Memoria LED:
  - `ws2812_periph.mem0.MEM[0]` hasta `MEM[15]` en el `.gtkw`.
  - El testbench dumpea hasta `MEM[62]`.

Conclusion: el `.gtkw` esta preparado para verificar exactamente lo que menciono el profesor: el cambio de la memoria del LED durante la simulacion.

## 10. Cambios en archivos `.init`

### `colorlight_i5_rom.init`

Cambio fuerte:

- Antes: 1379 lineas.
- Ahora: 214 lineas.

La reduccion indica que ya no se esta usando una imagen grande tipo BIOS/librerias completas para ese archivo raiz, sino una imagen ROM mucho mas acotada para el flujo no-BIOS de simulacion.

Esto coincide con el objetivo de que el procesador arranque directamente ejecutando firmware de prueba, sin esperar carga por serial/BIOS.

### `colorlight_i5_mem.init`

Se actualizo el identificador de texto de LiteX. El cambio parece ser solo de timestamp/identificador del SoC.

## 11. `colorlight_daniel.py`

Se agrego un SoC nuevo:

- Usa `board.colorlight_daniel`.
- Agrega fuentes de `Led_panel_12bpp`.
- Instancia `led_panel0`.
- Usa Ethernet RMII con `LiteEthPHYRMII`.

Este archivo parece relacionado con otro flujo o placa/periferico de panel LED, no con el flujo principal no-BIOS de `colorlight_i5_no_bios.py`. No lo tomaria como archivo central para arreglar la simulacion actual salvo que el profesor indique que ese es el nuevo target.

## 12. Para que se realizaron los cambios

Segun la comparacion, los cambios se hicieron para resolver los problemas que habiamos diagnosticado:

1. Evitar depender de BIOS en simulacion.
2. Asegurar que el firmware correcto se embeba en ROM.
3. Evitar que el simulador lea `.init` viejos o desde la carpeta equivocada.
4. Generar headers CSR antes de compilar firmware.
5. Compilar firmware no-BIOS real y verificar que quepa en ROM.
6. Simplificar el SoC durante simulacion deshabilitando SDRAM.
7. Activar `disp0`/WS2812 para tener una salida visible en ondas.
8. Registrar en VCD la memoria interna del LED.
9. Proveer un archivo GTKWave ya configurado con PC, multiplicador, estados y memoria LED.

## 13. Flujo recomendado despues del pull

Para revisar el flujo del profesor sin modificar codigo manualmente:

```bash
cd /home/andresrivera/digital_UN/Litex
./simulate.sh
```

Ese script prepara firmware, build e init files.

Para correr la simulacion completa por Makefile:

```bash
cd /home/andresrivera/digital_UN/Litex
make sim_lattice
```

Para abrir las ondas con la vista del profesor:

```bash
cd /home/andresrivera/digital_UN/Litex
gtkwave colorlight_i5_TB.vcd colorlight_i5_no_bios_sim.gtkw
```

Nota: no ejecute estos comandos en este reporte; solo compare los cambios del pull.

## 14. Archivos que ahora son los mas importantes

Para entender y depurar la simulacion nueva, miraria en este orden:

1. `Litex/Makefile`
2. `Litex/simulate.sh`
3. `Litex/colorlight_i5_no_bios.py`
4. `Litex/NO_bios_fw/main.c`
5. `Litex/colorlight_i5_TB.v`
6. `Litex/colorlight_i5_no_bios_sim.gtkw`
7. `Litex/colorlight_i5_rom.init`

## 15. Conclusion

El nuevo pull si apunta directamente a corregir la simulacion. En particular, corrige el punto mas critico detectado antes: el flujo no-BIOS ahora genera y copia explicitamente la ROM init que el testbench debe leer.

Tambien agrega evidencia visual para depuracion: `colorlight_i5_no_bios_sim.gtkw` incluye el PC del VexRiscv, las senales del multiplicador y la memoria del LED. Por eso, si el profesor dice que ya funcionan las simulaciones, la forma de confirmarlo es abrir ese `.gtkw` y verificar:

- el PC avanzando desde ROM,
- `mult_32.init`,
- `mult_32.done`,
- `mult_32.pp`,
- `disp0`/`ws2812_periph` iniciando,
- y cambios en `ws2812_periph.mem0.MEM[...]`.

La intencion del arreglo es clara: pasar de una simulacion dependiente de BIOS/rutas ambiguas a una simulacion no-BIOS reproducible con firmware embebido y ondas preparadas para inspeccionar el resultado.
