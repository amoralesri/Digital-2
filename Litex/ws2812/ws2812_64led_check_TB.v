`timescale 1ns/1ps

module ws2812_64led_check_TB;
    localparam integer N_LEDS       = 64;
    localparam integer BITS_PER_LED = 24;
    localparam integer TOTAL_BITS   = N_LEDS * BITS_PER_LED;

    reg         clk       = 1'b0;
    reg         reset     = 1'b1;
    reg         init_m    = 1'b0;
    reg         rst_cmd   = 1'b0;
    reg  [23:0] w_data    = 24'h000000;
    reg  [7:0]  w_address = 8'h00;
    reg         we_a      = 1'b0;
    wire        dout;
    wire        done;

    integer bit_count;
    integer high_count;
    integer frame_id;
    integer max_active_address;
    reg     prev_dout;

    ws2812_periph #(
        .SIZE(8),
        .N_LEDS(8'd64)
    ) uut (
        .reset(reset),
        .clk(clk),
        .init_m(init_m),
        .rst_cmd(rst_cmd),
        .w_data(w_data),
        .w_address(w_address),
        .we_a(we_a),
        .dout(dout),
        .done(done)
    );

    always #5 clk = ~clk;

    function [23:0] pixel_word;
        input integer frame;
        input integer index;
        reg [7:0] r;
        reg [7:0] g;
        reg [7:0] b;
        begin
            r = (frame == 0) ? (8'h10 + index[7:0]) : (8'h80 - index[7:0]);
            g = (frame == 0) ? (8'h40 ^ index[7:0]) : (8'h20 + index[7:0]);
            b = (frame == 0) ? (8'hc0 - index[7:0]) : (8'h55 ^ index[7:0]);
            pixel_word = {g, r, b}; // GRB wire order, transmitted MSB-first.
        end
    endfunction

    function expected_bit;
        input integer frame;
        input integer absolute_bit;
        integer led;
        integer bit_in_led;
        reg [23:0] word;
        begin
            led        = absolute_bit / BITS_PER_LED;
            bit_in_led = absolute_bit % BITS_PER_LED;
            word       = pixel_word(frame, led);
            expected_bit = word[23 - bit_in_led];
        end
    endfunction

    task write_pixel;
        input integer address;
        input [23:0] data;
        begin
            if (address >= N_LEDS)
                $fatal(1, "Attempted write outside framebuffer: %0d", address);
            @(negedge clk);
            w_address = address[7:0];
            w_data    = data;
            we_a      = 1'b1;
            @(negedge clk);
            we_a      = 1'b0;
        end
    endtask

    task load_frame;
        input integer frame;
        integer i;
        begin
            for (i = 0; i < N_LEDS; i = i + 1)
                write_pixel(i, pixel_word(frame, i));

            @(negedge clk);
            if (uut.mem0.MEM[0] !== pixel_word(frame, 0))
                $fatal(1, "MEM[0] mismatch for frame %0d: got %06x expected %06x",
                    frame, uut.mem0.MEM[0], pixel_word(frame, 0));
            if (uut.mem0.MEM[63] !== pixel_word(frame, 63))
                $fatal(1, "MEM[63] mismatch for frame %0d: got %06x expected %06x",
                    frame, uut.mem0.MEM[63], pixel_word(frame, 63));
        end
    endtask

    task clear_capture;
        input integer frame;
        begin
            frame_id           = frame;
            bit_count          = 0;
            high_count         = 0;
            max_active_address = 0;
            prev_dout          = dout;
        end
    endtask

    task start_and_wait_frame;
        input integer frame;
        integer i;
        begin
            clear_capture(frame);
            @(negedge clk);
            init_m = 1'b1;
            repeat (5) @(negedge clk);
            init_m = 1'b0;

            wait(done === 1'b0);
            wait(done === 1'b1);
            @(posedge clk);

            if (bit_count != TOTAL_BITS)
                $fatal(1, "Frame %0d transmitted %0d bits, expected %0d",
                    frame, bit_count, TOTAL_BITS);
            if (uut.count0.address !== 8'd63)
                $fatal(1, "Frame %0d final address %0d, expected 63",
                    frame, uut.count0.address);
            if (max_active_address != 63)
                $fatal(1, "Frame %0d max active address %0d, expected 63",
                    frame, max_active_address);

            for (i = 0; i < 3000; i = i + 1) begin
                @(posedge clk);
                if (dout !== 1'b0)
                    $fatal(1, "Frame %0d latch/reset low violated at cycle %0d", frame, i);
            end
        end
    endtask

    always @(posedge clk) begin
        if (reset) begin
            high_count <= 0;
            prev_dout  <= dout;
        end else begin
            if (uut.init_led) begin
                if (uut.count0.address >= N_LEDS)
                    $fatal(1, "LED %0d was started, expected maximum 63", uut.count0.address);
                if (uut.count0.address > max_active_address)
                    max_active_address <= uut.count0.address;
            end

            if (dout)
                high_count <= high_count + 1;

            if (prev_dout && !dout) begin
                if (bit_count >= TOTAL_BITS)
                    $fatal(1, "Extra data pulse after %0d bits", TOTAL_BITS);
                if (high_count == 24) begin
                    if (expected_bit(frame_id, bit_count) !== 1'b0)
                        $fatal(1, "Frame %0d bit %0d was 0, expected 1",
                            frame_id, bit_count);
                end else if (high_count == 48) begin
                    if (expected_bit(frame_id, bit_count) !== 1'b1)
                        $fatal(1, "Frame %0d bit %0d was 1, expected 0",
                            frame_id, bit_count);
                end else begin
                    $fatal(1, "Frame %0d bit %0d high count %0d, expected 24 or 48",
                        frame_id, bit_count, high_count);
                end
                bit_count  <= bit_count + 1;
                high_count <= 0;
            end

            prev_dout <= dout;
        end
    end

    initial begin
        $dumpfile("ws2812_64led_check_TB.vcd");
        $dumpvars(0, ws2812_64led_check_TB);

        repeat (5) @(negedge clk);
        reset = 1'b0;
        repeat (5) @(negedge clk);

        if (uut.count0.address !== 8'd0)
            $fatal(1, "Initial address is %0d, expected 0", uut.count0.address);

        load_frame(0);
        start_and_wait_frame(0);

        load_frame(1);
        if (uut.mem0.MEM[63] === pixel_word(0, 63))
            $fatal(1, "Second frame did not change MEM[63]");
        start_and_wait_frame(1);

        $display("PASS: 64 LEDs, 1536 bits/frame, GRB MSB-first, LED63, no LED64, second frame");
        $finish;
    end
endmodule
