# Digital UN

Este repositorio contiene ejemplos y prácticas de diseño digital, incluyendo programas en ensamblador RISC-V y módulos en Verilog.  
El flujo de trabajo está organizado en dos carpetas principales:

- **`asm/`** → programas en ensamblador y su Makefile para compilación.  
- **`rtl/`** → diseños en Verilog y su Makefile para simulación.  

---

## 🚀 Requisitos en Linux

Instala las siguientes herramientas antes de usar el repositorio:

```bash
sudo apt update
sudo apt install iverilog gtkwave make build-essential gcc-riscv64-unknown-elf
```
```
sudo ln -s $(which riscv64-unknown-elf-gcc) /usr/bin/riscv32-unknown-elf-gcc
sudo ln -s $(which riscv64-unknown-elf-ld) /usr/bin/riscv32-unknown-elf-ld
sudo ln -s $(which riscv64-unknown-elf-objdump) /usr/bin/riscv32-unknown-elf-objdump
sudo ln -s $(which riscv64-unknown-elf-objcopy) /usr/bin/riscv32-unknown-elf-objcopy
sudo ln -s $(which riscv64-unknown-elf-as)  /usr/bin/riscv32-unknown-elf-as
```

- **iverilog** → compilador y simulador de Verilog (Icarus Verilog).  
- **gtkwave** → visualización de señales (archivos `.vcd`).  
- **make** y **build-essential** → utilidades para compilar con los Makefiles.  
- **gcc-riscv64-unknown-elf** → compilador cruzado para ensamblador RISC-V.  

---
## Clonar github

a continuacion se clona el repositorio github para poder empezar a trabajar en el
```bash
git clone https://github.com/cicamargoba/digital_UN.git

```

## 🛠️ Uso

### 1. Ensamblador (asm)

Para compilar los programas en ensamblador:

```bash
cd digital_UN/femtoRV/basic/firmware/asm
```
ahora podemos agregar nuestro archivo .S para poder ejecutarlo, cambiamos las variables del makefile OBJECTS y OBJS
### Ejemplos
```bash
OBJS=for.o    # cambiar por el target del for
OBJECTS =  for.o     # por los archivos necesarios para ejecutar el programa
CROSS   = riscv32-unknown-elf
CC      = $(CROSS)-gcc
AS      = $(CROSS)-as
LD      = $(CROSS)-ld
OBJCOPY = $(CROSS)-objcopy
OBJDUMP = $(CROSS)-objdump
AFLAGS  = -march=rv32i -mabi=ilp32
```


---

### 2. Simulación en Verilog (rtl)

Para ejecutar la simulación del módulo de simulacion **quark**:

```bash
cd femtoRV/rtl
make sim_quark
```


El flujo realizará lo siguiente:
1. Compilar los archivos Verilog con **Icarus Verilog**.  
2. Ejecutar la simulación.  
3. Generar un archivo de trazas (`dump.vcd`).  

Puedes abrir el resultado con **GTKWave**:

```bash
gtkwave bench.vcd
```

---

### 3. Limpiar archivos generados

En cualquiera de las carpetas con Makefile (`asm/` o `rtl/`), puedes ejecutar:

```bash
make clean
```

para eliminar los archivos intermedios.