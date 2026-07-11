module led_mem_dual#(
    parameter addr_lenght = 8
) (
   input                           clk,
   input      [addr_lenght -1 :0]  address,
   output reg [23:0]               data_r,
//
   input                           we_a,
   input      [addr_lenght -1 :0]  w_address,
   input      [23:0]               w_data
);
    reg [23:0] MEM [0: (2**(addr_lenght) - 1)];
    integer init_i;
    integer init_file;

    initial begin
        for (init_i = 0; init_i < (2**addr_lenght); init_i = init_i + 1)
            MEM[init_i] = 24'h000000;
`ifndef SYNTHESIS
        init_file = $fopen("display.hex", "r");
        if (init_file) begin
            $fclose(init_file);
            $readmemh("display.hex", MEM);
        end
`endif
    end

    always @(posedge clk) begin
        data_r <= MEM[address];
    end

//------------------------------------------------------------------
// write port A
//------------------------------------------------------------------

    always @(negedge clk)
    begin
        if (we_a) begin
            MEM[w_address] <= w_data;
        end 
    end


endmodule
