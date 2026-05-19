`timescale 1ns / 1ps
`include "p0_pt1.v"

module tb_p0_pt1;

    // Entradas
    reg clk;
    reg rst;

    // Salidas
    wire green;
    wire yellow;
    wire red;

    // Instancia del DUT (Device Under Test)
    p0_pt1 dut (
        .clk(clk),
        .rst(rst),
        .green(green),
        .yellow(yellow),
        .red(red)
    );

    // Generación del reloj (Periodo = 10ns)
    always #5 clk = ~clk;

    initial begin
        // Archivo de ondas para visualizar en GTKWave
        $dumpfile("p0_pt1_wave.vcd");
        $dumpvars(0, tb_p0_pt1);

        // Inicializar señales
        clk = 0;
        rst = 1;

        // Mantener el reset por un par de ciclos
        #20;
        rst = 0;
        $display("[%0t] Reset liberado, iniciando semaforo en VERDE", $time);

        // Esperar a que haga por lo menos dos ciclos completos 
        // 1 ciclo del semáforo = 5vd + 2am + 4rj = 11 clocks = 110 ns
        // Dos ciclos = 22 clocks = 220 ns
        #250;
        
        $display("[%0t] Simulacion completada. Finalizando Testbench.", $time);
        $finish;
    end
endmodule
