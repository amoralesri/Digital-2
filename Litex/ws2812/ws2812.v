module ws2812 (
    input        clk,
    input        reset,
    input        init_t,
    input [1:0]  sel,
    output       dout,
    output       done_t
);

parameter FCLK_HZ = 60000000;
parameter T0H = 16'd24;    // 0.40 us @ 60 MHz.
parameter T1H = 16'd48;    // 0.80 us @ 60 MHz.
parameter PER = 16'd73;    // Measured bit period is PER + 2 cycles = 1.25 us.
parameter RES = 16'd3000;  // 50 us latch/reset @ 60 MHz.

wire rst;
wire inc;
wire  [1:0] sel_tim;
wire z;
wire [15:0] count_out;
wire [15:0] mux_out;


count_ws  count0 ( .clk(clk), .rst(rst), .inc(inc), .cnt_out(count_out) );
comp_ws   comp0  ( .in1(mux_out), .in2(count_out), .z(z) );
mux_ws    mux0   ( .in1(T0H), .in2(T1H), .in3(RES), .in4(PER), .sel(sel_tim), .y(mux_out) );
ctrl_ws   ctrl0  ( .clk(clk), .reset(reset), .init_t(init_t), .sel(sel), .z(z), 
                   .dout(dout), .done(done_t), .rst(rst), .inc(inc), .sel_tim(sel_tim) );

endmodule
