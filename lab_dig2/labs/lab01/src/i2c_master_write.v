`timescale 1ns / 1ps

module i2c_master_write #(
    parameter CLKS_PER_HALF_SCL = 5
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       start,
    input  wire [6:0] address,
    input  wire [7:0] data_in,
    output reg        scl,
    inout  wire       sda,
    output reg        busy,
    output reg        done
);

    localparam [2:0] IDLE         = 3'd0;
    localparam [2:0] START        = 3'd1;
    localparam [2:0] SEND_ADDRESS = 3'd2;
    localparam [2:0] WAIT_ACK_1   = 3'd3;
    localparam [2:0] SEND_DATA    = 3'd4;
    localparam [2:0] WAIT_ACK_2   = 3'd5;
    localparam [2:0] STOP         = 3'd6;
    localparam [2:0] DONE         = 3'd7;

    localparam integer CLK_CNT_W = (CLKS_PER_HALF_SCL <= 1) ? 1 : $clog2(CLKS_PER_HALF_SCL);

    reg [2:0] state_reg, state_next;
    reg [6:0] address_reg, address_next;
    reg [7:0] data_reg, data_next;
    reg [7:0] shift_reg, shift_next;
    reg [2:0] bit_count, bit_count_next;
    reg [CLK_CNT_W-1:0] clk_count, clk_count_next;
    reg                 phase_reg, phase_next;
    reg                 stop_phase_reg, stop_phase_next;
    reg                 ack_received, ack_received_next;
    reg                 sda_out;
    reg                 sda_oe;

    wire       sda_in;
    wire       scl_tick;
    wire [2:0] state;

    assign sda      = sda_oe ? sda_out : 1'bz;
    assign sda_in   = sda;
    assign scl_tick = (clk_count == CLKS_PER_HALF_SCL - 1);
    assign state    = state_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state_reg      <= IDLE;
            address_reg    <= 7'd0;
            data_reg       <= 8'd0;
            shift_reg      <= 8'd0;
            bit_count      <= 3'd0;
            clk_count      <= {CLK_CNT_W{1'b0}};
            phase_reg      <= 1'b0;
            stop_phase_reg <= 1'b0;
            ack_received   <= 1'b0;
        end else begin
            state_reg      <= state_next;
            address_reg    <= address_next;
            data_reg       <= data_next;
            shift_reg      <= shift_next;
            bit_count      <= bit_count_next;
            clk_count      <= clk_count_next;
            phase_reg      <= phase_next;
            stop_phase_reg <= stop_phase_next;
            ack_received   <= ack_received_next;
        end
    end

    always @(*) begin
        state_next      = state_reg;
        address_next    = address_reg;
        data_next       = data_reg;
        shift_next      = shift_reg;
        bit_count_next  = bit_count;
        phase_next      = phase_reg;
        stop_phase_next = stop_phase_reg;
        ack_received_next = ack_received;

        if (scl_tick) begin
            clk_count_next = {CLK_CNT_W{1'b0}};
        end else begin
            clk_count_next = clk_count + 1'b1;
        end

        scl     = 1'b1;
        busy    = 1'b0;
        done    = 1'b0;
        sda_oe  = 1'b0;
        sda_out = 1'b0;

        case (state_reg)
            IDLE: begin
                ack_received_next = 1'b0;
                phase_next        = 1'b0;
                stop_phase_next   = 1'b0;

                if (start) begin
                    address_next = address;
                    data_next    = data_in;
                    state_next   = START;
                end
            end

            START: begin
                busy    = 1'b1;
                sda_oe  = 1'b1;
                sda_out = 1'b0;
                phase_next      = 1'b0;
                stop_phase_next = 1'b0;

                if (scl_tick) begin
                    shift_next     = {address_reg, 1'b0};
                    bit_count_next = 3'd7;
                    state_next     = SEND_ADDRESS;
                end
            end

            SEND_ADDRESS: begin
                busy    = 1'b1;
                scl     = phase_reg;
                sda_oe  = ~shift_reg[7];
                sda_out = 1'b0;

                if (scl_tick) begin
                    if (phase_reg == 1'b0) begin
                        phase_next = 1'b1;
                    end else begin
                        phase_next = 1'b0;
                        if (bit_count == 3'd0) begin
                            state_next = WAIT_ACK_1;
                        end else begin
                            shift_next     = {shift_reg[6:0], 1'b0};
                            bit_count_next = bit_count - 1'b1;
                        end
                    end
                end
            end

            WAIT_ACK_1: begin
                busy    = 1'b1;
                scl     = phase_reg;
                sda_oe  = 1'b0;
                sda_out = 1'b0;

                if (scl_tick) begin
                    if (phase_reg == 1'b0) begin
                        phase_next = 1'b1;
                    end else begin
                        phase_next        = 1'b0;
                        ack_received_next = (sda_in == 1'b0);

                        if (sda_in == 1'b0) begin
                            shift_next     = data_reg;
                            bit_count_next = 3'd7;
                            state_next     = SEND_DATA;
                        end else begin
                            stop_phase_next = 1'b0;
                            state_next      = STOP;
                        end
                    end
                end
            end

            SEND_DATA: begin
                busy    = 1'b1;
                scl     = phase_reg;
                sda_oe  = ~shift_reg[7];
                sda_out = 1'b0;

                if (scl_tick) begin
                    if (phase_reg == 1'b0) begin
                        phase_next = 1'b1;
                    end else begin
                        phase_next = 1'b0;
                        if (bit_count == 3'd0) begin
                            state_next = WAIT_ACK_2;
                        end else begin
                            shift_next     = {shift_reg[6:0], 1'b0};
                            bit_count_next = bit_count - 1'b1;
                        end
                    end
                end
            end

            WAIT_ACK_2: begin
                busy    = 1'b1;
                scl     = phase_reg;
                sda_oe  = 1'b0;
                sda_out = 1'b0;

                if (scl_tick) begin
                    if (phase_reg == 1'b0) begin
                        phase_next = 1'b1;
                    end else begin
                        phase_next        = 1'b0;
                        ack_received_next = (sda_in == 1'b0);
                        stop_phase_next   = 1'b0;
                        state_next        = STOP;
                    end
                end
            end

            STOP: begin
                busy   = 1'b1;
                sda_oe = 1'b1;

                if (stop_phase_reg == 1'b0) begin
                    sda_oe  = 1'b1;
                    sda_out = 1'b0;
                    if (scl_tick) begin
                        stop_phase_next = 1'b1;
                    end
                end else begin
                    sda_oe  = 1'b0;
                    sda_out = 1'b0;
                    if (scl_tick) begin
                        state_next = DONE;
                    end
                end
            end

            DONE: begin
                done          = 1'b1;
                phase_next    = 1'b0;
                stop_phase_next = 1'b0;
                state_next    = IDLE;
            end

            default: begin
                state_next = IDLE;
            end
        endcase
    end

endmodule
