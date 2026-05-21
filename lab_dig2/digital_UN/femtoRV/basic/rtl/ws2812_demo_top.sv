`timescale 1ns / 1ps

module ws2812_demo_top (
    input  logic clk,
    input  logic resetn,
    output logic ws2812_dout
);

    localparam logic [31:0] REFRESH_CYCLES = 32'd1_250_000; // 50 ms at 25 MHz.

    typedef enum logic [0:0] {
        ST_START_FRAME,
        ST_WAIT_FRAME
    } state_t;

    state_t      state_q;
    state_t      state_d;
    logic [31:0] refresh_count_q;
    logic [31:0] refresh_count_d;
    logic        rst;
    logic        init_m;
    logic        done_m;

    assign rst = !resetn;

    send_N_LEDS #(
        .N_LEDS(64)
    ) u_leds (
        .clk_i    (clk),
        .rst_i    (rst),
        .init_m_i (init_m),
        .dout_o   (ws2812_dout),
        .done_m_o (done_m)
    );

    always_ff @(posedge clk) begin
        if (rst) begin
            state_q         <= ST_START_FRAME;
            refresh_count_q <= 32'd0;
        end else begin
            state_q         <= state_d;
            refresh_count_q <= refresh_count_d;
        end
    end

    always @* begin
        state_d         = state_q;
        refresh_count_d = refresh_count_q;

        case (state_q)
            ST_START_FRAME: begin
                if (refresh_count_q != 32'd0) begin
                    refresh_count_d = refresh_count_q - 32'd1;
                end else begin
                    state_d = ST_WAIT_FRAME;
                end
            end

            ST_WAIT_FRAME: begin
                if (done_m) begin
                    refresh_count_d = REFRESH_CYCLES;
                    state_d         = ST_START_FRAME;
                end
            end

            default: begin
                state_d         = ST_START_FRAME;
                refresh_count_d = 32'd0;
            end
        endcase
    end

    always @* begin
        init_m = (state_q == ST_START_FRAME) && (refresh_count_q == 32'd0);
    end

endmodule
