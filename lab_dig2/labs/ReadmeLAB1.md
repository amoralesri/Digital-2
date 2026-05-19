# Lab01 – Implementación de un Protocolo de Comunicación I²C (Master – Write)

## Contenido

- Objetivos de aprendizaje  
- Fundamento teórico  
- Descripción del sistema  
- Arquitectura del diseño  
- Actividades del laboratorio  
- Entregables  
- Preguntas de reflexión  

---

# 1. Objetivos de aprendizaje

Al finalizar esta práctica, el estudiante será capaz de:

- Comprender el funcionamiento básico del **protocolo I²C**.
- Analizar la secuencia de comunicación entre un **master** y un **slave**.
- Diseñar una **Máquina de Estado Algorítmica (ASM)** para implementar un protocolo.
- Implementar un **controlador I²C Master básico en Verilog**.
- Verificar el funcionamiento del sistema mediante **simulación en GTKWave**.

---

# 2. Fundamento teórico

## 2.1 Protocolo I²C

El protocolo **I²C (Inter-Integrated Circuit)** es un protocolo de comunicación serial síncrono utilizado para la comunicación entre dispositivos electrónicos dentro de un sistema.

Este protocolo utiliza dos líneas:

| Señal | Función |
|------|--------|
| **SCL** | Reloj generado por el master |
| **SDA** | Línea de datos bidireccional |

El bus I²C permite conectar múltiples dispositivos utilizando una estructura **master-slave**.

---

## 2.2 Estructura de una transmisión I²C

Una transacción típica sigue la siguiente secuencia:

START → ADDRESS → R/W → ACK → DATA → ACK → STOP

Donde:

- **START** inicia la comunicación.
- **ADDRESS** identifica el dispositivo esclavo.
- **R/W** indica operación de lectura o escritura.
- **ACK** confirma recepción del dato.
- **DATA** corresponde al byte transmitido.
- **STOP** finaliza la comunicación.

---

## 2.3 Condiciones especiales del protocolo

### Condición START

La condición START ocurre cuando:

SDA cambia de **alto a bajo** mientras **SCL permanece en alto**.

---

### Condición STOP

La condición STOP ocurre cuando:

SDA cambia de **bajo a alto** mientras **SCL permanece en alto**.

---

## 2.4 Transmisión de bits

Durante la transmisión:

- Los datos cambian cuando **SCL = 0**.
- El dato es válido cuando **SCL = 1**.

El receptor lee el dato cuando la señal **SCL está en alto**.

---

# 3. Descripción del sistema a implementar

En este laboratorio se implementará un **controlador I²C Master simplificado** capaz de realizar una operación de escritura.

La transacción que deberá generar el sistema será:

1. Generar condición **START**
2. Enviar **dirección del dispositivo (7 bits)**
3. Enviar **bit de escritura (0)**
4. Esperar **ACK**
5. Enviar **byte de datos**
6. Esperar **ACK**
7. Generar **STOP**

Para simplificar el diseño del laboratorio se asumirán las siguientes condiciones:

- Solo se implementará la operación **WRITE**
- Se transmitirá **un solo byte de datos**
- No se implementará **clock stretching**
- El **ACK será simulado desde el testbench**

---

# 4. Arquitectura del sistema

El sistema se dividirá en dos bloques principales:

## 4.1 Control (ASM)

El control se implementará mediante una **Máquina de Estado Algorítmica**.

Estados sugeridos:

- IDLE  
- START  
- SEND_ADDRESS  
- WAIT_ACK_1  
- SEND_DATA  
- WAIT_ACK_2  
- STOP  
- DONE  

La ASM será responsable de:

- Generar condiciones **START y STOP**
- Controlar el envío de bits
- Administrar el conteo de bits
- Coordinar la recepción del ACK

---

## 4.2 Datapath

El datapath incluirá:

- Registro de dirección
- Registro de datos
- Registro de desplazamiento
- Contador de bits
- Generador de reloj para **SCL**

El bloque de control utilizará estos elementos para ejecutar el algoritmo del protocolo.

---

# 5. Actividades del laboratorio

## Parte 1 – Análisis del protocolo

Analice el diagrama temporal de una comunicación I²C.

Identifique:

- Condición START
- Transmisión de dirección
- Transmisión de datos
- Recepción de ACK
- Condición STOP

---

## Parte 2 – Diseño de la ASM

Diseñe la **Máquina de Estado Algorítmica** que controlará la comunicación.

El diseño debe incluir:

- Estados del sistema
- Acciones en cada estado
- Condiciones de transición

Se recomienda representar el diseño mediante un **diagrama de estados** o **diagrama ASM**.

---

## Parte 3 – Implementación en Verilog

Implemente el módulo correspondiente al **controlador I²C Master**.

El módulo debe incluir:

- Señales de reloj y reset
- Señal de inicio de transmisión
- Dirección del dispositivo
- Dato a transmitir
- Señales del bus **SCL** y **SDA**
- Señales de estado del sistema (`busy`, `done`)

---

## Parte 4 – Simulación

Desarrolle un **testbench** que:

- Genere el reloj del sistema
- Aplique el reset inicial
- Active la señal `start`
- Proporcione valores de dirección y datos
- Simule el bit **ACK** del dispositivo esclavo

---

## Parte 5 – Análisis en GTKWave

Analice la simulación utilizando **GTKWave**.

En la simulación deben observarse claramente las señales:

- `SCL`
- `SDA`
- `state`
- `bit_count`
- `shift_reg`
- `busy`
- `done`

La secuencia observada debe corresponder a:

START → ADDRESS → ACK → DATA → ACK → STOP

---

# 6. Entregables

Cada grupo deberá entregar:

- Código Verilog del controlador I²C Master  
- Testbench de simulación  
- Archivo de simulación (`.vcd`)  
- README que incluya:
  - Descripción de la ASM
  - Explicación de la simulación
  - Capturas de GTKWave

---

# 7. Preguntas de reflexión

1. ¿Por qué el protocolo I²C utiliza una línea bidireccional para datos?  
2. ¿Cuál es la función del bit **ACK**?  
3. ¿Qué ocurriría si dos masters intentan usar el bus simultáneamente?  
4. ¿Cómo cambiaría el diseño si se implementara una operación de **lectura (READ)**?
