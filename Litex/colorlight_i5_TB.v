`timescale 1ns / 1ps
`define SIMULATION

module colorlight_i5_TB();
// Testbench uses a 10 MHz clock
// Want to interface to 115200 baud UART
// 25000000 / 115200 = 217 Clocks Per Bit.
parameter tck              = 40;
parameter c_BIT_PERIOD     = 8680;
parameter enable_vcd       = 1;
parameter dump_all_design  = 0;
parameter sim_cycles       = 100000;
parameter finish_on_ws_done = 0;
parameter finish_after_ws_done_edges = 1;
parameter [7:0] sim_n_leds = 8'd64;

   reg       CLK;
   reg       RESET;
   reg       RXD;
   wire      TXD;
   
   colorlight_i5 uut(
    .clk25(CLK),
    .cpu_reset_n(!RESET),
    .serial_tx(TXD),
    .serial_rx(RXD)
   );

    defparam uut.ws2812_periph.N_LEDS = sim_n_leds;

    integer csr_writes;
    integer max_csr_write_addr;
    integer ws_done_edges;
    initial begin
        csr_writes = 0;
        max_csr_write_addr = 0;
        ws_done_edges = 0;
    end
    // Generación de clock principal
    initial begin
        CLK = 0;
        forever #(tck/2) CLK = ~CLK; // 1MHz clock
    end

  // Takes in input byte and serializes it 
  task UART_WRITE_BYTE;
    input [7:0] i_Data;
    integer     ii;
    begin
       
      // Send Start Bit
      RXD <= 1'b0;
      #(c_BIT_PERIOD);
      #1000;
       
       
      // Send Data Byte
      for (ii=0; ii<8; ii=ii+1)
        begin
          RXD <= i_Data[ii];
          #(c_BIT_PERIOD);
        end
       
      // Send Stop Bit
      RXD <= 1'b1;
      #(c_BIT_PERIOD);
     end
  endtask // UART_WRITE_BYTE


    // Inicialización de las señales de control
    initial begin
        #0   RXD   = 1;
        #0   RESET = 1;
        #80  RESET = 1;
        RESET = 0;
    end

    integer idx; 
    initial begin

    if (enable_vcd) begin
        $dumpfile("colorlight_i5_TB.vcd");
        if (dump_all_design) begin
            $dumpvars(-1,colorlight_i5_TB);
        end else begin
            $dumpvars(0, colorlight_i5_TB.CLK);
            $dumpvars(0, colorlight_i5_TB.RESET);
            $dumpvars(0, colorlight_i5_TB.uut.VexRiscv.lastStagePc);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_cyc);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_stb);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_ack);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_we);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_adr);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_dat_w);
            $dumpvars(0, colorlight_i5_TB.uut.basesoc_dbus_dat_r);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.init_m);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.done);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.dout);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.w_address);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.w_data);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.we_a);
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.address);
        end

        for(idx = 0; idx < 64; idx = idx +1)
            $dumpvars(0, colorlight_i5_TB.uut.ws2812_periph.mem0.MEM[idx]);
    end
    //$dumpvars(0, bench.uut.CPU.registerFile[10],bench);

    //for(idx = 0; idx < 50; idx = idx +1)  $dumpvars(0, bench.uut.dpram_p0.dpram0.ram[idx]);
    //$dumpvars(0, bench.uut.CPU.registerFile[10],bench);


    #(tck*sim_cycles)
    $display("Simulation stop: PC=%08x disp0_done=%b disp0_addr=%0d MEM[0]=%06x MEM[63]=%06x",
        colorlight_i5_TB.uut.VexRiscv.lastStagePc,
        colorlight_i5_TB.uut.ws2812_periph.done,
        colorlight_i5_TB.uut.ws2812_periph.address,
        colorlight_i5_TB.uut.ws2812_periph.mem0.MEM[0],
        colorlight_i5_TB.uut.ws2812_periph.mem0.MEM[63]);
    $finish;
 end

    always @(posedge uut.ws2812_periph.we_a) begin
        csr_writes = csr_writes + 1;
        if (uut.ws2812_periph.w_address > max_csr_write_addr)
            max_csr_write_addr = uut.ws2812_periph.w_address;
        $display("CSR->WS2812 write %0d: addr=%0d data=%06x t=%0t",
            csr_writes,
            uut.ws2812_periph.w_address,
            uut.ws2812_periph.w_data,
            $time);
    end

    always @(posedge uut.ws2812_periph.done) begin
        ws_done_edges = ws_done_edges + 1;
        $display("CSR WS2812 DONE EDGE: ws_done_edges=%0d csr_writes=%0d max_addr=%0d ws_addr=%0d mem0=%06x mem63=%06x t=%0t",
            ws_done_edges,
            csr_writes,
            max_csr_write_addr,
            uut.ws2812_periph.address,
            uut.ws2812_periph.mem0.MEM[0],
            uut.ws2812_periph.mem0.MEM[63],
            $time);
        if (finish_on_ws_done && (ws_done_edges >= finish_after_ws_done_edges)) begin
            #(tck*4);
            $display("CSR path completed: csr_writes=%0d max_addr=%0d ws_done_edges=%0d MEM[0]=%06x MEM[63]=%06x",
                csr_writes,
                max_csr_write_addr,
                ws_done_edges,
                uut.ws2812_periph.mem0.MEM[0],
                uut.ws2812_periph.mem0.MEM[63]);
            $finish;
        end
    end
 
 


/*





    // Transmisión serial de los datos



*/

endmodule   
 
