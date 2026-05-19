`timescale 1ns / 1ps

module p0_pt2 (
    input  wire       clk,
    input  wire       rst,
    input  wire       start,
    input  wire [3:0] x,
    output reg  [5:0] acc,
    output reg        done
);

    // Definición de estados (FSM)
    localparam IDLE = 2'd0;
    localparam LOAD = 2'd1;
    localparam ADD  = 2'd2;
    localparam DONE = 2'd3;

    reg [1:0] state_reg, state_next;
    
    // Registros del datapath
    reg [5:0] acc_reg, acc_next;
    reg [1:0] count_reg, count_next; // Cuenta de 0 a 3 (4 sumas en total)

    // 1. Registro de Estado y Datapath (Secuencial)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state_reg <= IDLE;
            acc_reg   <= 6'd0;
            count_reg <= 2'd0;
        end else begin
            state_reg <= state_next;
            acc_reg   <= acc_next;
            count_reg <= count_next;
        end
    end

    // 2. Lógica Combinacional de Estado Siguiente y Datapath
    always @(*) begin
        // Valores por defecto para evitar latches
        state_next = state_reg;
        acc_next   = acc_reg;
        count_next = count_reg;
        
        // Salidas por defecto
        acc  = acc_reg;
        done = 1'b0;

        case (state_reg)
            IDLE: begin
                if (start)
                    state_next = LOAD;
            end
            
            LOAD: begin
                // Inicializa el acumulador y contador
                acc_next   = 6'd0;
                count_next = 2'd0;
                state_next = ADD;
            end
            
            ADD: begin
                // Suma el valor de la entrada 'x'
                acc_next = acc_reg + x;
                
                // Si hemos sumado 4 veces (0, 1, 2, 3), terminamos. 
                // Note que la comparamos antes de incrementar para que sume exactamente 4 veces
                if (count_reg == 2'd3) begin
                    state_next = DONE;
                end else begin
                    count_next = count_reg + 1'b1;
                end
            end
            
            DONE: begin
                // Señal de finalización
                done = 1'b1;
                state_next = IDLE;
            end
            
            default: state_next = IDLE;
        endcase
    end

endmodule
