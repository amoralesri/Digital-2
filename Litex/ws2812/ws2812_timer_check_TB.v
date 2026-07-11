`timescale 1ns / 1ps

module ws2812_timer_check_TB;
    reg        clk    = 1'b0;
    reg        reset  = 1'b1;
    reg        init_t = 1'b0;
    reg  [1:0] sel    = 2'b00;
    wire       dout;
    wire       done_t;

    localparam integer EXPECT_T0H_HIGH = 24;
    localparam integer EXPECT_T1H_HIGH = 48;
    localparam integer EXPECT_BIT_TOTAL = 75;
    localparam integer EXPECT_RESET_LOW_MIN = 3000;

    ws2812 dut (
        .clk    (clk),
        .reset  (reset),
        .init_t (init_t),
        .sel    (sel),
        .dout   (dout),
        .done_t (done_t)
    );

    always #10 clk = ~clk;

    task send_and_measure;
        input [1:0]  bit_sel;
        input [31:0] expected_high;
        input [31:0] expected_total;
        input        check_total_exact;
        integer high_cycles;
        integer total_cycles;
        begin
            high_cycles = 0;
            total_cycles = 0;
            sel = bit_sel;

            @(negedge clk);
            init_t = 1'b1;
            @(negedge clk);
            init_t = 1'b0;

            while (done_t !== 1'b1) begin
                @(posedge clk);
                total_cycles = total_cycles + 1;
                if (dout)
                    high_cycles = high_cycles + 1;
            end

            if (high_cycles !== expected_high) begin
                $display("ERROR: sel=%0d high_cycles=%0d expected=%0d",
                    bit_sel, high_cycles, expected_high);
                $fatal;
            end

            if (check_total_exact && (total_cycles !== expected_total)) begin
                $display("ERROR: sel=%0d total_cycles=%0d expected=%0d",
                    bit_sel, total_cycles, expected_total);
                $fatal;
            end

            if (!check_total_exact && (total_cycles < expected_total)) begin
                $display("ERROR: sel=%0d total_cycles=%0d minimum=%0d",
                    bit_sel, total_cycles, expected_total);
                $fatal;
            end

            $display("PASS: sel=%0d high_cycles=%0d total_cycles=%0d",
                bit_sel, high_cycles, total_cycles);
            repeat (3) @(posedge clk);
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        reset = 1'b0;
        repeat (2) @(posedge clk);

        send_and_measure(2'b00, EXPECT_T0H_HIGH, EXPECT_BIT_TOTAL, 1'b1);
        send_and_measure(2'b01, EXPECT_T1H_HIGH, EXPECT_BIT_TOTAL, 1'b1);
        send_and_measure(2'b10, 0, EXPECT_RESET_LOW_MIN, 1'b0);

        $display("PASS: ws2812 timer protocol check completed");
        $finish;
    end
endmodule
