`timescale 1ns / 1ps

module p0_pt3 #(
    parameter CLKS_PER_BIT = 8
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       start,
    input  wire [7:0] data_in,
    
    output reg        tx,
    output reg        busy,
    output reg        done
);

    // 1. Estados de la ASM (FSM de Control)
    localparam IDLE     = 2'd0;
    localparam LOAD     = 2'd1;
    localparam TRANSMIT = 2'd2;
    localparam DONE     = 2'd3;

    reg [1:0] state_reg, state_next;

    // 2. Registros del Datapath
    reg [7:0] shift_reg, shift_next;
    reg [2:0] bit_count, bit_count_next; // Cuenta los 8 bits (de 0 a 7)
    
    // El tick_cnt necesita contar hasta CLKS_PER_BIT - 1
    // Usamos $clog2 para calcular el ancho en bits dinámicamente
    reg [$clog2(CLKS_PER_BIT)-1 : 0] tick_cnt, tick_next;

    // --- Bloque Secuencial (Actualización de registros) ---
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state_reg <= IDLE;
            shift_reg <= 8'd0;
            bit_count <= 3'd0;
            tick_cnt  <= 0;
        end else begin
            state_reg <= state_next;
            shift_reg <= shift_next;
            bit_count <= bit_count_next;
            tick_cnt  <= tick_next;
        end
    end

    // --- Bloque Combinacional (Estado Siguiente, Datapath y Salidas) ---
    always @(*) begin
        // Valores por defecto (mantener el estado/valor)
        state_next     = state_reg;
        shift_next     = shift_reg;
        bit_count_next = bit_count;
        tick_next      = tick_cnt;
        
        // Salidas por defecto
        tx   = 1'b1; // Línea serie en reposo es '1'
        busy = 1'b0;
        done = 1'b0;

        case (state_reg)
            IDLE: begin
                if (start) begin
                    state_next = LOAD;
                end
            end
            
            LOAD: begin
                busy = 1'b1;
                // Cargar datos a los registros internos (Datapath)
                shift_next     = data_in;
                bit_count_next = 3'd0;
                tick_next      = 0;
                
                state_next = TRANSMIT;
            end
            
            TRANSMIT: begin
                busy = 1'b1;
                // Transmitir el bit menos significativo primero (LSB)
                tx = shift_reg[0];
                
                // Un "tick" cuenta los ciclos de reloj que debe durar cada bit
                if (tick_cnt == (CLKS_PER_BIT - 1)) begin
                    // Reiniciar contador de tiempo de bit
                    tick_next = 0;
                    
                    // Desplazar el registro 1 bit a la derecha (shift right)
                    shift_next = {1'b0, shift_reg[7:1]};
                    
                    // Comprobar si ya enviamos los 8 bits (del 0 al 7)
                    if (bit_count == 3'd7) begin
                        state_next = DONE;
                    end else begin
                        bit_count_next = bit_count + 1'b1;
                    end
                end else begin
                    // Seguir esperando la duración del bit
                    tick_next = tick_cnt + 1'b1;
                end
            end
            
            DONE: begin
                done = 1'b1;
                state_next = IDLE;
            end
            
            default: state_next = IDLE;
        endcase
    end

endmodule
