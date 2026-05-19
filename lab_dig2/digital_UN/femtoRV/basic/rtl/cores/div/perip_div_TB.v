`timescale 1ns / 1ps

`define SIMULATION
module peripheral_div_TB;
   reg clk;
   reg  reset;
   reg  start;
   reg [15:0]d_in;
   reg cs;
   reg [4:0]addr;
   reg rd;
   reg wr;
   reg printed;
   wire [31:0]d_out;

	peripheral_div uut (
		.clk(clk), 
		.reset(reset), 
		.d_in(d_in), 
		.cs(cs), 
		.addr(addr), 
		.rd(rd), 
		.wr(wr), 
		.d_out(d_out) 
	);

   parameter PERIOD = 20;
   // Initialize Inputs
   initial begin  
      clk = 0; reset = 0; d_in = 0; addr = 16'h0000; cs=0; rd=0; wr=0; printed = 0;
   end
   // clk generation
   initial         clk <= 0;
   always #(PERIOD/2) clk <= ~clk;

   initial begin 
    forever begin
     // Reset 
     @ (negedge clk);
	  reset = 1;
	  @ (negedge clk);
	  reset = 0;
     #(PERIOD*4)
     // A operator
	  cs=1; rd=0; wr=1;
	  d_in = 16'h0020;
	  addr = 16'h0004;
     #(PERIOD)
     cs=0; rd=0; wr=0;
     #(PERIOD*3)
     // B operator
	  cs=1; rd=0; wr=1;
	  d_in = 16'h000F;
	  addr = 16'h0008;
     #(PERIOD)
     cs=0; rd=0; wr=0;
     #(PERIOD*3)
     // Init signal
	  cs=1; rd=0; wr=1;
	  d_in = 16'h0001;
	  addr = 16'h000C;
     #(PERIOD)
     cs=0; rd=0; wr=0;
     #(PERIOD*70)
     // read done
     cs=1; rd=1; wr=0;
     addr = 16'h0014;
     #(PERIOD)
     cs=0; rd=0; wr=0;
     #(PERIOD)
     // read data	
     cs=1; rd=1; wr=0;
     addr = 16'h0010;
     #(PERIOD);
     cs=0; rd=0; wr=0;
     #(PERIOD*20);   
    end
   end
	 

   initial begin: TEST_CASE
     $dumpfile("perip_div_TB.vcd");
     $dumpvars(-1, peripheral_div_TB);
     #(PERIOD*160) $finish;
   end

   always @(posedge clk) begin
      if (uut.div1.done && !printed) begin
         $display("Peripheral div: %0d / %0d = quotient %0d (0x%04h), result bus 0x%08h",
                  uut.A, uut.B, uut.div1.result[15:0], uut.div1.result[15:0], uut.div1.result);
         printed = 1;
      end
   end

endmodule
