`timescale 1ns / 1ps
`include "p0_pt2.v"

module tb_p0_pt2;

    // Entradas
    reg       clk;
    reg       rst;
    reg       start;
    reg [3:0] x;

    // Salidas
    wire [5:0] acc;
    wire       done;

    // Instanciar el Device Under Test (DUT)
    p0_pt2 dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .x(x),
        .acc(acc),
        .done(done)
    );

    // Generación del reloj (Periodo = 10ns, Frecuencia = 100MHz)
    always #5 clk = ~clk;

    initial begin
        // Archivo de ondas para visualización en GTKWave
        $dumpfile("p0_pt2_wave.vcd");
        $dumpvars(0, tb_p0_pt2);

        // Inicializar entradas
        clk   = 0;
        rst   = 1;
        start = 0;
        x     = 4'd0;

        // Esperar unos ciclos y liberar el reset
        #20;
        rst = 0;
        #10;

        // --- Prueba 1: Sumar 3 cuatro veces (3*4 = 12) ---
        $display("[%0t] Iniciando Prueba 1: Sumar 3 cuatro veces", $time);
        x = 4'd3;
        start = 1;
        #10; // Mantener start por un ciclo
        start = 0;

        // Esperar a que 'done' se active
        wait (done == 1'b1);
        $display("[%0t] Prueba 1 Terminada. Valor Acumulado: %d (Esperado: 12)", $time, acc);
        #20; // Esperar en el IDLE

        // --- Prueba 2: Sumar 6 cuatro veces (6*4 = 24) ---
        $display("[%0t] Iniciando Prueba 2: Sumar 6 cuatro veces", $time);
        x = 4'd6;
        start = 1;
        #10;
        start = 0;

        // Esperar a que 'done' se active
        wait (done == 1'b1);
        $display("[%0t] Prueba 2 Terminada. Valor Acumulado: %d (Esperado: 24)", $time, acc);
        #40;
        
        $display("[%0t] Todas las simulaciones completadas con exito", $time);
        $finish; // Terminar simulación
    end

endmodule
