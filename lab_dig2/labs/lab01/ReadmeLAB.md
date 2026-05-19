# Lab01 - Implementación de un Protocolo de Comunicación I2C
## Master Write

## 1. Descripción general

En esta práctica se implementó un controlador I2C Master básico en Verilog. El diseño realiza una sola operación de escritura, enviando una dirección de 7 bits, el bit de escritura y un byte de datos.

La secuencia implementada fue:

```text
START -> ADDRESS + WRITE -> ACK -> DATA -> ACK -> STOP
```

Para mantener el diseño sencillo, solo se implementó la operación WRITE. No se incluyó lectura, clock stretching, arbitraje entre varios masters ni transmisión de varios bytes. El ACK del esclavo fue simulado desde el testbench.

---

## 2. Protocolo I2C aplicado

El protocolo I2C trabaja principalmente con dos señales:

- `SCL`: reloj generado por el master.
- `SDA`: línea de datos bidireccional.

En este laboratorio, el master genera la señal `SCL` y usa `SDA` para enviar la dirección y el dato. Después de cada byte, el master libera `SDA` para que el esclavo pueda responder con un ACK.

La condición `START` ocurre cuando `SDA` baja de `1` a `0` mientras `SCL` está en alto. La condición `STOP` ocurre cuando `SDA` sube de `0` a `1` mientras `SCL` está en alto.

Durante la transmisión, el dato cambia cuando `SCL` está en bajo y se mantiene estable cuando `SCL` está en alto.

---

## 3. Máquina de estados ASM

La comunicación se controló mediante una máquina de estados. Los estados implementados fueron:

| Estado | Descripción |
|---|---|
| `IDLE` | Estado de reposo. Espera la señal `start`. |
| `START` | Genera la condición de inicio del bus I2C. |
| `SEND_ADDRESS` | Envía la dirección del esclavo junto con el bit de escritura. |
| `WAIT_ACK_1` | Libera `SDA` y espera el ACK después de la dirección. |
| `SEND_DATA` | Envía el byte de datos. |
| `WAIT_ACK_2` | Libera `SDA` y espera el ACK después del dato. |
| `STOP` | Genera la condición de parada. |
| `DONE` | Finaliza la transmisión y vuelve a reposo. |

La codificación usada para los estados fue:

| Valor | Estado |
|---|---|
| `000` | `IDLE` |
| `001` | `START` |
| `010` | `SEND_ADDRESS` |
| `011` | `WAIT_ACK_1` |
| `100` | `SEND_DATA` |
| `101` | `WAIT_ACK_2` |
| `110` | `STOP` |
| `111` | `DONE` |

---

## 4. Datapath del diseño

El diseño usa algunos registros y contadores para poder realizar la transmisión de forma ordenada.

Los elementos principales son:

- `address_reg`: guarda la dirección de 7 bits.
- `data_reg`: guarda el dato que se va a transmitir.
- `shift_reg`: registro de desplazamiento para enviar los bits de izquierda a derecha, es decir, MSB primero.
- `bit_count`: contador para saber cuántos bits faltan por transmitir.
- `clk_count`: contador usado para generar una señal más lenta para `SCL`.
- `phase_reg`: controla la fase baja o alta de `SCL`.
- `sda_out`: valor que el master quiere poner en `SDA`.
- `sda_oe`: habilita o libera el control de `SDA`.

La línea `SDA` se manejó como bidireccional usando alta impedancia:

```verilog
assign sda = sda_oe ? sda_out : 1'bz;
assign sda_in = sda;
```

Esto permite que el master controle `SDA` cuando transmite, pero que también pueda soltar la línea durante los ACK.

---

## 5. Flujo de funcionamiento

Al inicio el sistema está en `IDLE`. En este estado `busy = 0`, `done = 0` y el módulo espera que se active `start`.

Cuando `start` se activa, el módulo pasa a `START`, genera la condición de inicio y carga internamente la dirección y el dato.

Luego se carga el registro de desplazamiento con:

```verilog
{address, 1'b0}
```

El último bit es `0` porque se trata de una operación de escritura.

Después, en `SEND_ADDRESS`, se envían los 8 bits correspondientes a la dirección más el bit de escritura. Al terminar, el master libera `SDA` y espera el primer ACK en `WAIT_ACK_1`.

Luego se carga el byte de datos en `shift_reg` y se transmite en el estado `SEND_DATA`. Después de esto se espera un segundo ACK en `WAIT_ACK_2`.

Finalmente, el módulo genera la condición `STOP`, activa `done` durante un ciclo y vuelve al estado `IDLE`.

---

## 6. Simulación

Para verificar el funcionamiento se realizó un testbench en Verilog. El testbench se encargó de generar el reloj, aplicar el reset, activar la señal `start`, asignar valores de dirección y dato, y simular los ACK del esclavo.

Los valores usados en la simulación fueron:

```verilog
address = 7'b1010000;
data_in = 8'hA5;
```

Con estos valores, el primer byte enviado es:

```text
{address, 1'b0} = 1010_0000 = 8'hA0
```

Luego se transmite el dato:

```text
data_in = 8'hA5
```

El ACK se simuló haciendo que el testbench coloque `SDA = 0` durante los estados `WAIT_ACK_1` y `WAIT_ACK_2`.

También se usó un `pullup` en `SDA`, ya que en I2C la línea sube a `1` cuando ningún dispositivo la está forzando a `0`.

---

## 7. Comandos usados

Los comandos usados para compilar, ejecutar y abrir la simulación fueron:

```bash
iverilog -o sim_i2c tb_i2c_master_write.v i2c_master_write.v
vvp sim_i2c
gtkwave i2c_master_write.vcd
```

El primer comando compila el diseño y el testbench.  
El segundo ejecuta la simulación.  
El tercero abre el archivo `.vcd` en GTKWave.

---

## 8. Señales revisadas en GTKWave

En GTKWave se revisaron las siguientes señales:

- `clk`
- `rst`
- `start`
- `scl`
- `sda`
- `busy`
- `done`
- `state_reg`
- `bit_count`
- `shift_reg`

En la simulación se observó que la máquina de estados avanzó por la secuencia esperada:

```text
START -> ADDRESS + WRITE -> ACK -> DATA -> ACK -> STOP
```

También se observó que `bit_count` cuenta desde `111` hasta `000` durante el envío de la dirección y luego vuelve a contar desde `111` hasta `000` durante el envío del dato.

El registro `shift_reg` primero toma el valor `A0`, que corresponde a la dirección más el bit de escritura, y después toma el valor `A5`, que corresponde al dato transmitido.

---

## 9. Captura de la simulación

En la siguiente captura se muestra la simulación en GTKWave:

```text
Insertar aquí la captura de GTKWave
```

La forma de onda permite verificar que `busy` se activa durante la comunicación, que `done` se activa al finalizar, y que la FSM pasa por los estados correspondientes a dirección, ACK, dato, ACK y parada.

---

## 10. Análisis de resultados

La simulación muestra que el controlador cumple con la secuencia básica solicitada para una escritura I2C.

Primero el módulo permanece en reposo hasta que se activa `start`. Luego genera la condición `START` y comienza la transmisión. Durante la primera parte se envía `8'hA0`, que corresponde a la dirección `7'b1010000` junto con el bit de escritura `0`.

Después se libera `SDA` para recibir el primer ACK. Luego se transmite el dato `8'hA5`, se espera el segundo ACK y finalmente se genera la condición `STOP`.

Al terminar la comunicación, `busy` vuelve a cero y `done` se activa para indicar que la transmisión finalizó correctamente.

---

## 11. Preguntas de reflexión

### ¿Por qué el protocolo I2C utiliza una línea bidireccional para datos?

Porque la misma línea `SDA` se usa para enviar y recibir información. En este laboratorio, el master usa `SDA` para enviar la dirección y el dato, pero también debe liberar esa línea para que el esclavo pueda responder con el ACK.

### ¿Cuál es la función del bit ACK?

El ACK confirma que el byte anterior fue recibido. En I2C, el receptor responde colocando `SDA = 0` después de recibir un byte.

### ¿Qué ocurriría si dos masters intentan usar el bus simultáneamente?

Podría presentarse un conflicto en el bus, ya que dos dispositivos intentarían controlar las señales al mismo tiempo. En una implementación completa de I2C se necesita arbitraje para resolver esta situación. En esta práctica ese caso no se implementó.

### ¿Cómo cambiaría el diseño si se implementara una operación de lectura?

Para una operación de lectura se tendría que enviar el bit `R/W = 1`. Después de eso, el master debería liberar `SDA` para que el esclavo sea quien coloque los bits de datos en la línea. También sería necesario agregar estados para recibir el dato y para que el master responda con ACK o NACK.

---

## 12. Archivos entregados

- `i2c_master_write.v`: módulo principal del controlador I2C Master Write.
- `tb_i2c_master_write.v`: testbench de simulación.
- `i2c_master_write.vcd`: archivo de ondas generado para GTKWave.
- `README.md`: descripción del diseño, simulación y resultados.
