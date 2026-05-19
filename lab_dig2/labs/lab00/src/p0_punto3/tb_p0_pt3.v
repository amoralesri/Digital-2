`timescale 1ns / 1ps
`include "p0_pt3.v"

module tb_p0_pt3;

    // Frecuencia equivalente a 100MHz
    localparam CLK_PERIOD = 10;
    
    // Enviar cada bit por 8 ciclos tal como recomienda la guia (80 ns por bit)
    localparam BIT_DURATION = 8; 

    // Entradas
    reg       clk;
    reg       rst;
    reg       start;
    reg [7:0] data_in;

    // Salidas
    wire tx;
    wire busy;
    wire done;

    // Instanciar DUT
    p0_pt3 #(
        .CLKS_PER_BIT(BIT_DURATION)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .data_in(data_in),
        .tx(tx),
        .busy(busy),
        .done(done)
    );

    // Generador de reloj
    always #(CLK_PERIOD/2) clk = ~clk;

    // Procedimiento de prueba
    initial begin
        // Archivos para GTKWave
        $dumpfile("p0_pt3_wave.vcd");
        $dumpvars(0, tb_p0_pt3);

        // Inicialización de señales
        clk     = 0;
        rst     = 1;
        start   = 0;
        data_in = 8'h00;

        // Reset
        #(CLK_PERIOD * 3);
        rst = 0;
        #(CLK_PERIOD * 2);

        // --------------------------------------------------------
        // Prueba 1: Transmitir dato 8'hA5 (10100101 en binario)
        // --------------------------------------------------------
        $display("[%0t] Iniciando Prueba 1: Dato de entrada 8'hA5", $time);
        
        // Configurar dato de entrada y activar Start
        data_in = 8'hA5; 
        start   = 1;
        #(CLK_PERIOD);   // Un pulso de reloj de start
        start   = 0;

        // Esperamos a que la transmisión termine (monitorizamos done)
        wait(done == 1'b1);
        $display("[%0t] ==== Fin transmision 1 ====", $time);
        
        // Dar algo de tiempo "muerto" entre transmisiones para ver la zona de IDLE en la onda
        #(CLK_PERIOD * 15);

        // --------------------------------------------------------
        // Prueba 2: Transmitir dato 8'h3C (00111100 en binario)
        // --------------------------------------------------------
        $display("[%0t] Iniciando Prueba 2: Dato de entrada 8'h3C", $time);
        
        data_in = 8'h3C;
        start   = 1;
        #(CLK_PERIOD);
        start   = 0;

        wait(done == 1'b1);
        $display("[%0t] ==== Fin transmision 2 ====", $time);
        
        #(CLK_PERIOD * 10);
        $display("[%0t] Simulacion completada con exito.", $time);
        $finish;
    end

endmodule
