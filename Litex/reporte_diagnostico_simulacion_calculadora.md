# Reporte de diagnostico: simulacion calculadora/multiplicador LiteX

Fecha: 2026-06-16  
Repositorio inspeccionado: `/home/andresrivera/digital_UN`  
Zona principal: `/home/andresrivera/digital_UN/Litex`

## 1. Mapa del repositorio

El area relevante para la simulacion de la calculadora/multiplicador esta en `Litex/`.

- `Litex/`: contiene los SoC Colorlight, testbench de SoC, archivos `.init`, firmware y perifericos.
- `Litex/firmware/`: firmware pensado para el flujo con BIOS/carga por `litex_term`.
- `Litex/NO_bios_fw/`: firmware pensado para flujo no-BIOS, es decir, arrancar directamente desde memoria inicializada.
- `Litex/build/colorlight_i5/`: build principal usado por los Makefiles actuales.
- `Litex/build/gateware/`: segundo arbol de build paralelo, con otro set de gateware e init files.
- `Litex/mult/`: modulo multiplicador en Verilog, wrapper Migen/LiteX, Makefile y testbenches unitarios.
- `Litex/ws2812/` y `Litex/Led_panel_12bpp/`: perifericos/display; no son centrales para la correccion del multiplicador.
- `migen_tutorial/`, `femtoRV/`, `basic_circuits/`: material de clase y ejemplos; no parecen necesarios para tocar el flujo del multiplicador en `Litex/`.

## 2. Archivos relevantes encontrados

### SoC LiteX

- `Litex/colorlight_i5.py`: SoC normal con BIOS.
- `Litex/colorlight_i5_no_bios.py`: variante no-BIOS. Define `integrated_rom_size`, `cpu_reset_address = 0x00000000` y usa `NO_bios_fw/firmware.bin` si existe.
- `Litex/board/colorlight_i5.py`: plataforma Colorlight i5 y pines.

### Firmware C

- `Litex/firmware/main.c`: firmware actual de calculadora/multiplicador, enlazado para correr desde `main_ram`.
- `Litex/NO_bios_fw/main.c`: firmware no-BIOS de prueba del multiplicador. Escribe operandos fijos en los CSR.
- `Litex/firmware/Makefile`: compila `firmware/firmware.bin`.
- `Litex/NO_bios_fw/Makefile`: compila `NO_bios_fw/firmware.bin` y genera `firmware.lst`.

### Linker y regiones de memoria

- `Litex/firmware/linker.ld`: ubica `.text` y `.rodata` en `main_ram`.
- `Litex/NO_bios_fw/linker.ld`: ubica `.text` y `.rodata` en `rom`, con `.data` y `.bss` en `sram`.
- `Litex/build/colorlight_i5/software/include/generated/regions.ld`: regiones generadas del SoC:
  - `rom`: `0x00000000`
  - `sram`: `0x10000000`
  - `spiflash`: `0x00800000`
  - `main_ram`: `0x40000000`
  - `csr`: `0xf0000000`

### Inicializacion de memoria

- `Litex/colorlight_i5_rom.init`
- `Litex/colorlight_i5_sram.init`
- `Litex/colorlight_i5_mem.init`
- `Litex/build/colorlight_i5/gateware/colorlight_i5_rom.init`
- `Litex/build/colorlight_i5/gateware/colorlight_i5_sram.init`
- `Litex/build/colorlight_i5/gateware/colorlight_i5_mem.init`
- `Litex/build/gateware/colorlight_i5_rom.init`
- `Litex/build/gateware/colorlight_i5_sram.init`
- `Litex/build/gateware/colorlight_i5_mem.init`

Hay varias copias de los `.init`, y no todas coinciden.

### Simulacion y testbench

- `Litex/colorlight_i5_TB.v`: testbench del SoC.
- `Litex/build/colorlight_i5/gateware/colorlight_i5.v`: gateware generado.
- `Litex/build/gateware/colorlight_i5.v`: otro gateware generado.
- `Litex/mult/mult_32_TB.v`: testbench unitario del multiplicador.
- `Litex/mult/perip_mult_32_TB.v`: testbench de periferico del multiplicador.
- `Litex/mult/*.gtkw`: configuraciones GTKWave del multiplicador.

### Calculadora/multiplicador

- `Litex/mult/mult_32.py`: wrapper Migen/LiteX con CSR.
- `Litex/mult/mult_32.v`: top Verilog del multiplicador.
- `Litex/mult/control_mult.v`: FSM del multiplicador.
- `Litex/mult/acc.v`, `Litex/mult/lsr_mult.v`, `Litex/mult/rsr.v`, `Litex/mult/comp.v`: datapath.

### CSR

- `Litex/build/colorlight_i5/software/include/generated/csr.h`
- `Litex/build/software/include/generated/csr.h`
- `Litex/csr.csv`

Los CSR relevantes son:

- `CSR_MULT0__A_ADDR = CSR_BASE + 0x1800`
- `CSR_MULT0__B_ADDR = CSR_BASE + 0x1804`
- `CSR_MULT0_INIT_ADDR = CSR_BASE + 0x1808`
- `CSR_MULT0_PP_ADDR = CSR_BASE + 0x180c`
- `CSR_MULT0_DONE_ADDR = CSR_BASE + 0x1810`

## 3. Flujo actual de compilacion del firmware

`Litex/firmware/Makefile` usa:

- `BUILD_DIR=../build/colorlight_i5/`
- `-T linker.ld`
- objetos: `crt0.o isr.o helpers.o main.o uart.o`

El firmware existente `Litex/firmware/firmware.elf` esta enlazado para correr desde `main_ram`:

- entry point: `0x40000000`
- `.text`: `0x40000000`
- `.data`: `0x10000000`
- stack: fin de `sram`, alrededor de `0x10002000`

Conclusion: `Litex/firmware/firmware.bin` corresponde al flujo con BIOS/carga en RAM, no al flujo no-BIOS de simulacion directa desde ROM.

## 4. Flujo actual de inicializacion de memoria

El gateware generado contiene `$readmemh` con nombres relativos:

```verilog
$readmemh("colorlight_i5_rom.init", rom);
$readmemh("colorlight_i5_sram.init", sram);
$readmemh("colorlight_i5_mem.init", mem);
```

Esto significa que el archivo que se carga depende del directorio desde donde se ejecute `vvp`.

Se encontro una inconsistencia importante:

- `Litex/colorlight_i5_rom.init`: 1379 lineas.
- `Litex/build/colorlight_i5/gateware/colorlight_i5_rom.init`: 9376 lineas.
- `Litex/build/gateware/colorlight_i5_rom.init`: 9376 lineas.

Ademas, actualmente no existe `Litex/NO_bios_fw/firmware.bin`, por lo que la variante `colorlight_i5_no_bios.py` no puede embeber un firmware no-BIOS nuevo sin antes compilarlo.

## 5. Flujo actual de simulacion

`Litex/colorlight_i5_TB.v` instancia:

```verilog
colorlight_i5 uut(
  .clk25(CLK),
  .cpu_reset_n(!RESET)
);
```

El testbench:

- genera clock,
- aplica reset,
- genera `colorlight_i5_TB.vcd`,
- termina tras un tiempo fijo,
- no envia datos por UART.

No se encontro un Makefile de simulacion de SoC que fije claramente:

- que gateware usar,
- desde que directorio ejecutar `vvp`,
- que `.init` copiar o leer.

Esto es riesgoso porque el gateware lee `.init` por ruta relativa.

## 6. Ubicacion de la calculadora/multiplicador

El wrapper LiteX esta en `Litex/mult/mult_32.py`.

Define:

- `_A`: `CSRStorage(16)`
- `_B`: `CSRStorage(16)`
- `_init`: `CSRStorage(1)`
- `_pp`: `CSRStatus(32)`
- `_done`: `CSRStatus(1)`

Instancia el Verilog:

```python
Instance("mult_32",
    i_clk  = ClockSignal("sys"),
    i_rst  = ResetSignal("sys"),
    i_init = self._init.storage,
    i_A    = self._A.storage,
    i_B    = self._B.storage,
    o_pp   = self._pp.status,
    o_done = self._done.status,
)
```

El modulo top Verilog esta en `Litex/mult/mult_32.v`.

La FSM esta en `Litex/mult/control_mult.v` con estados:

- `START`
- `CHECK`
- `SHIFT`
- `ADD`
- `END`

`done` vale 1 solo en `END`.

## 7. Como se controla desde C

En `Litex/firmware/main.c`, la funcion de acceso al hardware hace:

```c
csr_write_simple(a & 0xffff, CSR_MULT0__A_ADDR);
csr_write_simple(b & 0xffff, CSR_MULT0__B_ADDR);

csr_write_simple(1, CSR_MULT0_INIT_ADDR);
csr_write_simple(0, CSR_MULT0_INIT_ADDR);

while((csr_read_simple(CSR_MULT0_DONE_ADDR) & 0x1) == 0);

return csr_read_simple(CSR_MULT0_PP_ADDR);
```

En el firmware no-BIOS `Litex/NO_bios_fw/main.c`, la prueba actual escribe:

```c
mult0__A_write(0x10);
mult0__B_write(0x20);
mult0_init_write(1);
mult0_init_write(0);
while(mult0_done_read() == 0);
c = mult0_pp_read();
```

Eso prueba `0x10 * 0x20`, que da `0x200` decimal `512`, no `200`.

## 8. Posibles causas del fallo

1. El firmware usado por simulacion no es el correcto.
   `firmware/firmware.elf` esta enlazado a `0x40000000`, pero la simulacion arranca desde ROM en `0x00000000`.

2. El testbench puede estar leyendo un `.init` viejo o equivocado.
   Como `$readmemh` usa rutas relativas, ejecutar desde `Litex/` o desde `Litex/build/colorlight_i5/gateware/` cambia el archivo leido.

3. No existe `NO_bios_fw/firmware.bin`.
   La variante no-BIOS solo embebe ese archivo si existe.

4. Se mezclan builds.
   Hay `Litex/build/colorlight_i5/` y `Litex/build/`, ambos con `gateware`, `csr.h`, `regions.ld` e init files.

5. La simulacion puede seguir corriendo BIOS.
   El `colorlight_i5_rom.init` de build parece corresponder a `bios.bin`.

6. El firmware puede quedarse esperando `done`.
   Esto pasaria si el CPU no llega a escribir CSR, si los CSR no coinciden con el gateware simulado, o si la FSM no llega a `END`.

7. El resultado puede ser correcto pero la prueba esperada distinta.
   El firmware no-BIOS usa `0x10 * 0x20 = 512`; si se espera `10 * 20 = 200`, hay que cambiar operandos.

## 9. Plan minimo de correccion

### Caso 1: firmware no cargado en memoria correcta

Usar el flujo no-BIOS:

1. Generar headers/gateware base con `colorlight_i5_no_bios.py`.
2. Compilar `NO_bios_fw/firmware.bin`.
3. Reconstruir el SoC no-BIOS para embeber ese binario en ROM.

Verificar con `readelf` que el firmware no-BIOS tenga entry point `0x00000000`.

### Caso 2: testbench lee init viejo

Crear o usar un flujo de simulacion con cwd fijo.

La opcion mas segura es ejecutar la simulacion desde el directorio donde estan:

- `colorlight_i5.v`
- `colorlight_i5_rom.init`
- `colorlight_i5_sram.init`
- `colorlight_i5_mem.init`

o copiar explicitamente los `.init` correctos al directorio desde donde corre `vvp`.

### Caso 3: programa enlazado para direccion incorrecta

Para no-BIOS:

- `.text` debe estar en `rom`.
- `cpu_reset_address` debe ser `0x00000000`.
- `colorlight_i5_rom.init` debe contener el firmware no-BIOS, no BIOS.

### Caso 4: firmware corre pero se queda en BIOS/UART/puts

Confirmar en VCD o PC que no esta ejecutando BIOS.

Si el PC cae en simbolos de BIOS como `serialboot`, `readline`, `puts` o `uart_read`, el init de ROM no es el firmware no-BIOS correcto.

### Caso 5: firmware escribe CSR pero multiplicador no activa done

Mirar en GTKWave:

- `csr_bankarray_csrbank2_A0_re`
- `_A_storage`
- `_B_storage`
- `init_storage`
- `done_status`
- `pp_status`
- estado interno de `control_mult`

### Caso 6: periferico calcula pero resultado no se lee correctamente

Confirmar:

- direccion `0xf000180c` para `pp`,
- ancho de `pp_status`,
- valor esperado `200` o `512`,
- orden de escrituras CSR.

## 10. Archivos que NO tocaria

No tocaria manualmente:

- `Litex/build/**`, salvo regeneracion controlada.
- `Litex/VexRiscv.v`.
- `Litex/lattice_sim/**`.
- `migen_tutorial/**`.
- `femtoRV/**`.
- `basic_circuits/**`.
- `Litex/ws2812/**`.
- `Litex/Led_panel_12bpp/**`.
- headers generados como `csr.h`, `soc.h`, `regions.ld`, salvo regeneracion por LiteX.

## 11. Preguntas o ambiguedades antes de modificar

1. Desde que carpeta se esta ejecutando la simulacion: `Litex/`, `Litex/build/colorlight_i5/gateware/` u otra?
2. Cual es el comando exacto de simulacion usado actualmente?
3. La prueba esperada debe ser `10 * 20 = 200` o se acepta la prueba actual `0x10 * 0x20 = 512`?
4. Se quiere una simulacion no-BIOS pura o tambien conservar el flujo con BIOS para carga por `litex_term`?

## Conclusion

El problema mas probable no esta inicialmente en la FSM del multiplicador, sino en la cadena firmware-linker-init-simulacion:

- el firmware de `Litex/firmware` esta enlazado para `main_ram`,
- la simulacion arranca desde ROM,
- no existe actualmente `NO_bios_fw/firmware.bin`,
- hay varias copias de `.init`,
- y `$readmemh` carga archivos por nombre relativo.

La correccion minima deberia enfocarse primero en hacer reproducible el flujo no-BIOS y asegurar que el testbench lea exactamente la ROM init generada a partir del firmware correcto.
