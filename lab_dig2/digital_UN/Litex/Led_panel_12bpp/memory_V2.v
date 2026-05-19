module memory#(
    parameter size = 2047,
    parameter width = 11
)(
  input              clk,
  input  [width:0]   address,
  input              rd,
  output reg [23:0]  rdata,
  input              we_a,
  input  [11:0]      w_address,
  input  [23:0]      w_data
);

reg [11:0] MEM0 [0:size/2];
reg [11:0] MEM1 [0:size/2];

initial begin
    $readmemh("./image0.hex",MEM0);
    $readmemh("./image1.hex",MEM1);
end

  always @(negedge clk) begin
    if(rd) begin
        rdata[23:12] <= MEM0[address[10:0]];     //{RGB0,RGB1}
    end
  end
  always @(negedge clk) begin
    if(rd) begin
        rdata[11:0] <= MEM1[address[10:0]];     //{RGB0,RGB1}
    end
  end



//------------------------------------------------------------------
// write port A
//------------------------------------------------------------------


always @(negedge clk)
begin
//	if (en_a) begin
		  if (we_a) begin
        if(~w_address[11])
			    MEM0[w_address[10:0]] <= w_data;
        else
          MEM1[w_address[10:0]] <= w_data;
		  end 
//      dat_a_out<=MEM[w_address];
//	end 
end

endmodule
