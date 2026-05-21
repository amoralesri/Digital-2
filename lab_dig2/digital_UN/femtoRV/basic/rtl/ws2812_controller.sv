`timescale 1ns / 1ps

// ===== MODULO 1: send =====
module send (
    input  logic       clk_i,
    input  logic       rst_i,
    input  logic       init_t_i,
    input  logic [1:0] sel_i,
    output logic       dout_o,
    output logic       done_t_o
);

    localparam logic [31:0] FCM_FPGA = 32'd25_000_000;
    localparam logic [31:0] T0H      = 32'd10;
    localparam logic [31:0] T1H      = 32'd20;
    localparam logic [31:0] T0L      = 32'd21;
    localparam logic [31:0] T1L      = 32'd11;
    localparam logic [31:0] PER      = 32'd31;
    localparam logic [31:0] RES      = 32'd1250;

    typedef enum logic [0:0] {
        ST_IDLE,
        ST_SEND
    } state_t;

    state_t      state_q;
    state_t      state_d;
    logic [1:0]  sel_q;
    logic [1:0]  sel_d;
    logic [31:0] count_q;
    logic [31:0] count_d;
    logic [31:0] terminal_count;
    logic [31:0] high_count;
    logic [31:0] next_count;
    logic        dout_d;
    logic        done_t_d;

    always_ff @(posedge clk_i) begin
        if (rst_i) begin
            state_q  <= ST_IDLE;
            sel_q    <= 2'b00;
            count_q  <= 32'd0;
            dout_o   <= 1'b0;
            done_t_o <= 1'b0;
        end else begin
            state_q  <= state_d;
            sel_q    <= sel_d;
            count_q  <= count_d;
            dout_o   <= dout_d;
            done_t_o <= done_t_d;
        end
    end

    always @* begin
        terminal_count = (sel_q == 2'b10) ? (RES - 32'd1) : (PER - 32'd1);
        state_d = state_q;

        case (state_q)
            ST_IDLE: begin
                if (init_t_i) begin
                    state_d = ST_SEND;
                end
            end

            ST_SEND: begin
                if (count_q >= (terminal_count - 32'd1)) begin
                    state_d = ST_IDLE;
                end
            end

            default: begin
                state_d = ST_IDLE;
            end
        endcase
    end

    always @* begin
        high_count = (sel_q == 2'b01) ? T1H : T0H;
        next_count = count_q + 32'd1;

        sel_d      = sel_q;
        count_d    = count_q;
        dout_d     = 1'b0;
        done_t_d   = 1'b0;

        case (state_q)
            ST_IDLE: begin
                count_d = 32'd0;
                if (init_t_i) begin
                    sel_d    = sel_i;
                    count_d  = 32'd0;
                    dout_d   = (sel_i == 2'b10) ? 1'b0 : 1'b1;
                end
            end

            ST_SEND: begin
                count_d  = next_count;
                dout_d   = (sel_q != 2'b10) && (next_count < high_count);
                done_t_d = (next_count == terminal_count);
            end

            default: begin
                sel_d    = 2'b00;
                count_d  = 32'd0;
                dout_d   = 1'b0;
                done_t_d = 1'b0;
            end
        endcase
    end

endmodule


// ===== MODULO 2: ws2812 =====
module ws2812 (
    input  logic        clk_i,
    input  logic        rst_i,
    input  logic        init_i,
    input  logic [23:0] rgb_i,
    output logic        rst_cmd_o,
    output logic        dout_o,
    output logic        done_o
);

    typedef enum logic [0:0] {
        ST_IDLE,
        ST_WAIT_SEND
    } state_t;

    state_t      state_q;
    state_t      state_d;
    logic [23:0] shift_q;
    logic [23:0] shift_d;
    logic [4:0]  bit_count_q;
    logic [4:0]  bit_count_d;
    logic        init_t;
    logic [1:0]  sel_t;
    logic        done_t;
    logic        done_d;
    logic        rst_cmd_d;

    send u_send_bit (
        .clk_i    (clk_i),
        .rst_i    (rst_i),
        .init_t_i (init_t),
        .sel_i    (sel_t),
        .dout_o   (dout_o),
        .done_t_o (done_t)
    );

    always_ff @(posedge clk_i) begin
        if (rst_i) begin
            state_q     <= ST_IDLE;
            shift_q     <= 24'd0;
            bit_count_q <= 5'd0;
            done_o      <= 1'b0;
            rst_cmd_o   <= 1'b0;
        end else begin
            state_q     <= state_d;
            shift_q     <= shift_d;
            bit_count_q <= bit_count_d;
            done_o      <= done_d;
            rst_cmd_o   <= rst_cmd_d;
        end
    end

    always @* begin
        state_d = state_q;

        case (state_q)
            ST_IDLE: begin
                if (init_i) begin
                    state_d = ST_WAIT_SEND;
                end
            end

            ST_WAIT_SEND: begin
                if (done_t && (bit_count_q == 5'd0)) begin
                    state_d = ST_IDLE;
                end
            end

            default: begin
                state_d = ST_IDLE;
            end
        endcase
    end

    always @* begin
        shift_d     = shift_q;
        bit_count_d = bit_count_q;
        init_t      = 1'b0;
        sel_t       = 2'b00;
        done_d      = 1'b0;
        rst_cmd_d   = 1'b0;

        case (state_q)
            ST_IDLE: begin
                if (init_i) begin
                    shift_d     = rgb_i;
                    bit_count_d = 5'd23;
                    init_t      = 1'b1;
                    sel_t       = rgb_i[23] ? 2'b01 : 2'b00;
                end
            end

            ST_WAIT_SEND: begin
                if (done_t) begin
                    if (bit_count_q == 5'd0) begin
                        done_d    = 1'b1;
                        rst_cmd_d = 1'b1;
                    end else begin
                        shift_d     = {shift_q[22:0], 1'b0};
                        bit_count_d = bit_count_q - 5'd1;
                        init_t      = 1'b1;
                        sel_t       = shift_q[22] ? 2'b01 : 2'b00;
                    end
                end
            end

            default: begin
                shift_d     = 24'd0;
                bit_count_d = 5'd0;
                init_t      = 1'b0;
                sel_t       = 2'b00;
                done_d      = 1'b0;
                rst_cmd_d   = 1'b0;
            end
        endcase
    end

endmodule


// ===== MODULO 3: send_N_LEDS =====
module send_N_LEDS #(
    parameter int unsigned N_LEDS = 3
) (
    input  logic clk_i,
    input  logic rst_i,
    input  logic init_m_i,
    output logic dout_o,
    output logic done_m_o
);

    localparam int unsigned ADDR_W = (N_LEDS <= 1) ? 1 : $clog2(N_LEDS);

    typedef enum logic [1:0] {
        ST_IDLE,
        ST_WAIT_LED,
        ST_WAIT_RES
    } state_t;

    logic [23:0] led_mem [0:N_LEDS-1];

`ifdef WS2812_DEMO_INIT
    integer init_idx;

    initial begin
        for (init_idx = 0; init_idx < N_LEDS; init_idx = init_idx + 1) begin
            case (init_idx % 3)
                0: led_mem[init_idx] = 24'h00FF00; // Rojo
                1: led_mem[init_idx] = 24'hFF0000; // Verde
                default: led_mem[init_idx] = 24'h0000FF; // Azul
            endcase
        end
    end
`endif

    state_t             state_q;
    state_t             state_d;
    logic [ADDR_W:0]    addr_q;
    logic [ADDR_W:0]    addr_d;
    logic [ADDR_W:0]    next_addr;
    logic [23:0]        rgb_to_ws;
    logic               init_ws;
    logic               rst_cmd_ws;
    logic               done_ws;
    logic               dout_ws;
    logic               init_res;
    logic               done_res;
    logic               dout_res;
    logic               done_m_d;

    ws2812 u_ws2812 (
        .clk_i     (clk_i),
        .rst_i     (rst_i),
        .init_i    (init_ws),
        .rgb_i     (rgb_to_ws),
        .rst_cmd_o (rst_cmd_ws),
        .dout_o    (dout_ws),
        .done_o    (done_ws)
    );

    // Instancia dedicada para RES final; mantiene ws2812 enfocado solo en serializar 24 bits.
    send u_send_reset (
        .clk_i    (clk_i),
        .rst_i    (rst_i),
        .init_t_i (init_res),
        .sel_i    (2'b10),
        .dout_o   (dout_res),
        .done_t_o (done_res)
    );

    always_ff @(posedge clk_i) begin
        if (rst_i) begin
            state_q  <= ST_IDLE;
            addr_q   <= '0;
            done_m_o <= 1'b0;
        end else begin
            state_q  <= state_d;
            addr_q   <= addr_d;
            done_m_o <= done_m_d;
        end
    end

    always @* begin
        state_d = state_q;

        case (state_q)
            ST_IDLE: begin
                if (init_m_i) begin
                    state_d = ST_WAIT_LED;
                end
            end

            ST_WAIT_LED: begin
                if (rst_cmd_ws) begin
                    if (addr_q == (N_LEDS - 1)) begin
                        state_d = ST_WAIT_RES;
                    end else begin
                        state_d = ST_WAIT_LED;
                    end
                end
            end

            ST_WAIT_RES: begin
                if (done_res) begin
                    state_d = ST_IDLE;
                end
            end

            default: begin
                state_d = ST_IDLE;
            end
        endcase
    end

    always @* begin
        next_addr = addr_q + {{ADDR_W{1'b0}}, 1'b1};
        addr_d    = addr_q;
        init_ws   = 1'b0;
        init_res  = 1'b0;
        rgb_to_ws = led_mem[addr_q[ADDR_W-1:0]];
        done_m_d  = 1'b0;

        case (state_q)
            ST_IDLE: begin
                addr_d = '0;
                if (init_m_i) begin
                    rgb_to_ws = led_mem[0];
                    init_ws   = 1'b1;
                end
            end

            ST_WAIT_LED: begin
                if (rst_cmd_ws) begin
                    if (addr_q == (N_LEDS - 1)) begin
                        init_res = 1'b1;
                    end else begin
                        addr_d    = next_addr;
                        rgb_to_ws = led_mem[next_addr[ADDR_W-1:0]];
                        init_ws   = 1'b1;
                    end
                end
            end

            ST_WAIT_RES: begin
                if (done_res) begin
                    done_m_d = 1'b1;
                end
            end

            default: begin
                addr_d    = '0;
                init_ws   = 1'b0;
                init_res  = 1'b0;
                rgb_to_ws = led_mem[0];
                done_m_d  = 1'b0;
            end
        endcase
    end

    always @* begin
        if (state_q == ST_WAIT_RES) begin
            dout_o = dout_res;
        end else begin
            dout_o = dout_ws;
        end
    end

endmodule


`ifndef SYNTHESIS
// ===== TESTBENCH: tb_ws2812 =====
module tb_ws2812;

    localparam int unsigned CLK_PERIOD_NS = 40;
    localparam int unsigned N_LEDS_TB     = 3;
    localparam int unsigned TOTAL_BITS    = N_LEDS_TB * 24;
    localparam int unsigned RES_CYCLES    = 1250;

    logic clk_i;
    logic rst_i;
    logic init_m_i;
    logic dout_o;
    logic done_m_o;
    logic dout_prev;
    logic done_prev;
    logic [15:0] bit_edges;
    logic [15:0] low_run;
    logic [15:0] first_high_width;
    logic        first_bit_seen;
    logic        first_bit_done;
    logic        tb_error;

    send_N_LEDS #(
        .N_LEDS(N_LEDS_TB)
    ) dut (
        .clk_i    (clk_i),
        .rst_i    (rst_i),
        .init_m_i (init_m_i),
        .dout_o   (dout_o),
        .done_m_o (done_m_o)
    );

    initial begin
        clk_i = 1'b0;
        forever #(CLK_PERIOD_NS / 2) clk_i = ~clk_i;
    end

    initial begin
        $dumpfile("tb_ws2812.vcd");
        $dumpvars(0, tb_ws2812);
        $monitor("%0t clk_i=%0b dout_o=%0b done_m_o=%0b",
                 $time, clk_i, dout_o, done_m_o);

        rst_i    = 1'b1;
        init_m_i = 1'b0;

        // [DOC-2] pagina 5: bits[23:16]=Green, bits[15:8]=Red, bits[7:0]=Blue.
        dut.led_mem[0] = 24'h00FF00; // Rojo
        dut.led_mem[1] = 24'hFF0000; // Verde
        dut.led_mem[2] = 24'h0000FF; // Azul

        repeat (5) @(posedge clk_i);
        rst_i = 1'b0;

        repeat (2) @(posedge clk_i);
        init_m_i = 1'b1;
        @(posedge clk_i);
        init_m_i = 1'b0;
    end

    always @(posedge clk_i) begin
        if (rst_i) begin
            dout_prev        <= 1'b0;
            done_prev        <= 1'b0;
            bit_edges        <= 16'd0;
            low_run          <= 16'd0;
            first_high_width <= 16'd0;
            first_bit_seen   <= 1'b0;
            first_bit_done   <= 1'b0;
            tb_error         <= 1'b0;

            if (dout_o) begin
                $error("dout_o debe permanecer en 0 durante rst_i=1.");
                tb_error <= 1'b1;
            end
        end else begin
            dout_prev <= dout_o;
            done_prev <= done_m_o;

            if (dout_o && !dout_prev && (bit_edges < TOTAL_BITS)) begin
                bit_edges <= bit_edges + 16'd1;
                if (!first_bit_seen) begin
                    first_bit_seen   <= 1'b1;
                    first_high_width <= 16'd1;
                end
            end else if (first_bit_seen && !first_bit_done && dout_o) begin
                first_high_width <= first_high_width + 16'd1;
            end

            if (first_bit_seen && !first_bit_done && !dout_o && dout_prev) begin
                first_bit_done <= 1'b1;
                if (first_high_width != 16'd10) begin
                    $error("El primer bit debe ser 0 y medir T0H=10 ciclos; medido=%0d.",
                           first_high_width);
                    tb_error <= 1'b1;
                end
            end

            if (bit_edges >= TOTAL_BITS) begin
                if (!dout_o) begin
                    low_run <= low_run + 16'd1;
                end else begin
                    low_run <= 16'd0;
                end
            end

            if (done_m_o && done_prev) begin
                $error("done_m_o debe ser un pulso de exactamente 1 ciclo.");
                tb_error <= 1'b1;
            end

            if (done_m_o) begin
                if (bit_edges != TOTAL_BITS) begin
                    $error("Se esperaban 72 bits; transmitidos=%0d.", bit_edges);
                    tb_error <= 1'b1;
                end

                if (low_run < RES_CYCLES) begin
                    $error("RES debe mantener dout_o=0 por al menos 1250 ciclos; medido=%0d.",
                           low_run);
                    tb_error <= 1'b1;
                end

                if (!tb_error) begin
                    $display("SIMULACION COMPLETADA: todos los LEDs enviados.");
                end
                $finish;
            end
        end
    end

endmodule
`endif
