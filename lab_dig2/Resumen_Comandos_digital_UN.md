# Resumen de Comandos de Instalación - digital_UN

Este documento recopila todos los comandos ejecutados para instalar y configurar el entorno de trabajo fundamental para el repositorio `digital_UN`.

## 1. Clonación del Repositorio
```bash
git clone https://github.com/cicamargoba/digital_UN.git
```
*Propósito:* Clona la base de código que contiene los programas ASM y diseños RTL de Verilog sobre la cual vas a trabajar en tu proyecto.

## 2. Actualización de Punteros de Paquetes
```bash
sudo apt update
```
*Propósito:* Sincroniza y actualiza la lista de paquetes locales con la base de datos de los repositorios para garantizar que se descarguen las versiones más recientes.

## 3. Instalación de Herramientas Base
```bash
sudo apt install iverilog gtkwave make build-essential gcc-riscv64-unknown-elf -y
```
*Propósito:* Instala las dependencias y recursos principales que usa el repositorio:
- **iverilog**: Compilador y simulador principal de los archivos de Verilog (Icarus Verilog).
- **gtkwave**: Software para visualizar las señales de simulación (archivos `.vcd`).
- **make** y **build-essential**: Utilidades de Linux necesarias para compilar y automatizar flujos con los `Makefiles`.
- **gcc-riscv64-unknown-elf**: Compilador cruzado que permite compilar código (C y Ensamblador) para una arquitectura RISC-V en lugar de la arquitectura de tu sistema local.

## 4. Configuración de Enlaces Simbólicos (Toolchain)
```bash
sudo ln -s $(which riscv64-unknown-elf-gcc) /usr/bin/riscv32-unknown-elf-gcc
sudo ln -s $(which riscv64-unknown-elf-ld) /usr/bin/riscv32-unknown-elf-ld
sudo ln -s $(which riscv64-unknown-elf-objdump) /usr/bin/riscv32-unknown-elf-objdump
sudo ln -s $(which riscv64-unknown-elf-objcopy) /usr/bin/riscv32-unknown-elf-objcopy
sudo ln -s $(which riscv64-unknown-elf-as)  /usr/bin/riscv32-unknown-elf-as
```
*Propósito:* Crea alias (enlaces simbólicos) con la firma de 32 bits en las herramientas. Esto es extremadamente importante ya que el repositorio `digital_UN` busca llamar las dependencias como `riscv32-unknown-elf-...` explícitamente en el `Makefile`. Con este comando habilitas que la máquina de 64 bits conteste bajo el nombre de 32 bits a las solicitudes de ensamblado y compilación.

---
**Nota:** ¡Todo ha quedado instalado, configurado y validado en sus correspondientes ubicaciones!
