`timescale 1ns / 1ps

module p0_pt1(
    input  wire clk,
    input  wire rst,
    output reg  green,
    output reg  yellow,
    output reg  red
);

    // Definición de estados (FSM)
    localparam S0_VERDE    = 2'd0;
    localparam S1_AMARILLO = 2'd1;
    localparam S2_ROJO     = 2'd2;

    // Registros de la FSM y contador de ciclos
    reg [1:0] state_reg, state_next;
    reg [2:0] timer_reg, timer_next; // Contador máximo es 5, caben en 3 bits

    // 1. Logica secuencial (Actualización de registros)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state_reg <= S0_VERDE;
            timer_reg <= 3'd1; // Inicia contando el primer ciclo activo 
        end else begin
            state_reg <= state_next;
            timer_reg <= timer_next;
        end
    end

    // 2. Lógica combinacional (Estado Siguiente y Salidas)
    always @(*) begin
        // Valores por defecto
        state_next = state_reg;
        timer_next = timer_reg + 1'b1;
        
        green  = 1'b0;
        yellow = 1'b0;
        red    = 1'b0;

        case (state_reg)
            S0_VERDE: begin
                green = 1'b1;
                // Verde dura 5 ciclos. Si ya pasaron 5 ciclos, cambiamos a amarillo
                if (timer_reg == 3'd5) begin
                    state_next = S1_AMARILLO;
                    timer_next = 3'd1;
                end
            end
            
            S1_AMARILLO: begin
                yellow = 1'b1;
                // Amarillo dura 2 ciclos
                if (timer_reg == 3'd2) begin
                    state_next = S2_ROJO;
                    timer_next = 3'd1;
                end
            end
            
            S2_ROJO: begin
                red = 1'b1;
                // Rojo dura 4 ciclos
                if (timer_reg == 3'd4) begin
                    state_next = S0_VERDE;
                    timer_next = 3'd1;
                end
            end
            
            default: begin
                state_next = S0_VERDE;
                timer_next = 3'd1;
            end
        endcase
    end

endmodule
