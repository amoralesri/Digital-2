`timescale 1ns / 1ps

module tb_i2c_master_write;

    localparam CLK_PERIOD        = 10;
    localparam CLKS_PER_HALF_SCL = 5;

    localparam [2:0] WAIT_ACK_1 = 3'd3;
    localparam [2:0] WAIT_ACK_2 = 3'd5;

    reg        clk;
    reg        rst;
    reg        start;
    reg  [6:0] address;
    reg  [7:0] data_in;

    wire scl;
    wire sda;
    wire busy;
    wire done;

    wire slave_drive_ack;

    i2c_master_write #(
        .CLKS_PER_HALF_SCL(CLKS_PER_HALF_SCL)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .address(address),
        .data_in(data_in),
        .scl(scl),
        .sda(sda),
        .busy(busy),
        .done(done)
    );

    assign slave_drive_ack = (dut.state_reg == WAIT_ACK_1) || (dut.state_reg == WAIT_ACK_2);
    assign sda = slave_drive_ack ? 1'b0 : 1'bz;

    pullup(sda);

    always #(CLK_PERIOD / 2) clk = ~clk;

    initial begin
        $dumpfile("i2c_master_write.vcd");
        $dumpvars(0, tb_i2c_master_write);

        clk     = 1'b0;
        rst     = 1'b1;
        start   = 1'b0;
        address = 7'b1010000;
        data_in = 8'hA5;

        #(CLK_PERIOD * 4);
        rst = 1'b0;

        #(CLK_PERIOD * 3);
        start = 1'b1;
        #(CLK_PERIOD);
        start = 1'b0;

        wait(done == 1'b1);
        #(CLK_PERIOD * 6);

        $finish;
    end

endmodule
