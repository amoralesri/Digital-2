`timescale 1ns / 1ps
`define SIMULATION

module colorlight_i5_dma_TB();
    parameter tck = 40;
    parameter sim_cycles = 50000;
    parameter dump_all_design = 0;
    parameter enable_vcd = 0;
    parameter verbose_dma_bus = 0;
    parameter verbose_dma_events = 0;
    parameter verbose_heartbeat = 0;
    parameter finish_on_loader_done = 0;
    parameter finish_on_ws_done = 0;
    parameter finish_on_expected_writes = 0;
    parameter finish_on_both_done = 0;
    parameter enable_loader_watchdog = 0;
    parameter [7:0] sim_n_leds = 8'd64;
    parameter integer expected_dma_writes = 64;
    parameter integer finish_after_ws_done_edges = 1;

    reg  CLK;
    reg  RESET;
    reg  RXD;
    wire TXD;

    colorlight_i5 uut(
        .clk25(CLK),
        .cpu_reset_n(!RESET),
        .serial_tx(TXD),
        .serial_rx(RXD)
    );

    defparam uut.ws2812_periph.N_LEDS = sim_n_leds;

    wire [23:0] ws2812_mem0_0 = uut.ws2812_periph.mem0.MEM[0];
    wire [23:0] ws2812_mem0_1 = uut.ws2812_periph.mem0.MEM[1];
    wire [23:0] ws2812_mem0_2 = uut.ws2812_periph.mem0.MEM[2];
    wire [23:0] ws2812_mem0_3 = uut.ws2812_periph.mem0.MEM[3];
    wire [23:0] ws2812_mem0_4 = uut.ws2812_periph.mem0.MEM[4];
    wire [23:0] ws2812_mem0_5 = uut.ws2812_periph.mem0.MEM[5];
    wire [23:0] ws2812_mem0_6 = uut.ws2812_periph.mem0.MEM[6];
    wire [23:0] ws2812_mem0_7 = uut.ws2812_periph.mem0.MEM[7];

    // Aliases normales para observar la SRAM interna del SoC.
    // ws2812_buffer está en 0x10000000, que en Wishbone word-addressed
    // corresponde a 0x04000000 y cae en sram[0].
    wire [31:0] soc_sram_0 = uut.sram[0];
    wire [31:0] soc_sram_1 = uut.sram[1];
    wire [31:0] soc_sram_2 = uut.sram[2];
    wire [31:0] soc_sram_3 = uut.sram[3];
    wire [31:0] soc_sram_4 = uut.sram[4];
    wire [31:0] soc_sram_5 = uut.sram[5];
    wire [31:0] soc_sram_6 = uut.sram[6];
    wire [31:0] soc_sram_7 = uut.sram[7];

    initial begin
        CLK = 1'b0;
        forever #(tck/2) CLK = ~CLK;
    end

    initial begin
        RXD   = 1'b1;
        RESET = 1'b1;
        #80;
        RESET = 1'b0;
    end

    integer heartbeat_count;
    initial heartbeat_count = 0;

    integer idx;
    initial begin
        if (enable_vcd) begin
        $dumpfile("colorlight_i5_dma_TB.vcd");

        // Sistema completo: la CPU VexRiscv ejecuta NO_bios_fw_dma/firmware.bin.
        if (dump_all_design) begin
            // Dump completo: todos los módulos/señales bajo el SoC generado.
            // Ojo: el VCD puede crecer muchísimo y la simulación será más lenta.
            $dumpvars(-1, colorlight_i5_dma_TB.uut);

            // Icarus/GTKWave no siempre muestra memorias internas completas con
            // $dumpvars(-1, ...), así que volcamos explícitamente las primeras
            // posiciones de la RAM de video del periférico WS2812.
            for (idx = 0; idx < 8; idx = idx + 1)
                $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.MEM[idx]);

            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_0);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_1);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_2);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_3);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_4);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_5);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_6);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_7);

            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_0);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_1);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_2);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_3);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_4);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_5);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_6);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_7);
        end else begin
            // Dump reducido para poder observar DMA/loader sin generar un VCD gigante.
            $dumpvars(0, colorlight_i5_dma_TB.CLK);
            $dumpvars(0, colorlight_i5_dma_TB.RESET);
            // PC/pipeline internos del VexRiscv necesarios para correlacionar
            // el bloqueo del CPU con las transacciones Wishbone.
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.IBusCachedPlugin_fetchPc_pcReg);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.IBusCachedPlugin_fetchPc_pc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.decode_PC);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.execute_PC);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.memory_PC);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.writeBack_PC);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.lastStagePc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.VexRiscv.CsrPlugin_mepc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ibus_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ibus_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ibus_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ibus_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ibus_dat_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_dat_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_dbus_dat_w);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_request);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_grant);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_shared_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_shared_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_shared_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_shared_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_slave_sel);
            $dumpvars(0, colorlight_i5_dma_TB.uut.socbushandler_slave_sel_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface0_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface0_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface0_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface0_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface1_re);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface1_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.interface1_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_sel);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_re);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_w);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_interface1_bank_bus_dat_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_interface1_bank_bus_dat_w);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_interface1_bank_bus_re);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_interface1_bank_bus_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.subfragments_wishbonedmareader_state);
            $dumpvars(0, colorlight_i5_dma_TB.uut.subfragments_wishbonedmareader_next_state);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_enable_storage);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_length_storage);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_offset1);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_sink_sink_valid);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_sink_sink_ready);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_sink_sink_last);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_sink_sink_payload_address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_fifo_level);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_fifo_sink_ready);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_fifo_sink_valid);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_fifo_sink_last);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_fifo_source_last);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_dma_bus_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_dma_bus_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_dma_bus_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_dma_bus_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_dma_bus_dat_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_bus_ram_bus_cyc);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_bus_ram_bus_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_bus_ram_bus_ack);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_bus_ram_bus_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_adr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.basesoc_ram_dat_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_source_source_valid);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_source_source_ready);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_source_source_last);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_source_source_payload_data);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_sink_valid);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_sink_ready);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_sink_last);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_sink_payload_data);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_w_address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_w_data);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_busy);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_done);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_done_status1);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_re);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_done_we);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_dma_done);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_init_storage);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_init_wr_stb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_done_status0);
            $dumpvars(0, colorlight_i5_dma_TB.uut.disp0_start_storage);
            $dumpvars(0, colorlight_i5_dma_TB.uut.csr_bankarray_csrbank1_loader_start_re);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.done);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.dout);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.init_m);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.rst_cmd);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.w_data);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.w_address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.we_a);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.rgb);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.init_led);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.done_led);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.rst_addr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.inc_addr);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.z);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.clk);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.w_address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.w_data);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.we_a);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.address);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.data_r);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.init_m);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.done_led);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.z);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.done);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.init_led);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.rst);
            $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.ctrl0.inc);

            for (idx = 0; idx < 8; idx = idx + 1)
                $dumpvars(0, colorlight_i5_dma_TB.uut.ws2812_periph.mem0.MEM[idx]);

            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_0);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_1);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_2);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_3);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_4);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_5);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_6);
            $dumpvars(0, colorlight_i5_dma_TB.ws2812_mem0_7);

            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_0);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_1);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_2);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_3);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_4);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_5);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_6);
            $dumpvars(0, colorlight_i5_dma_TB.soc_sram_7);
        end
        end
    end

    integer writes;
    initial writes = 0;

    integer cycles_since_write;
    initial cycles_since_write = 0;

    integer dump_snapshot_count;
    initial dump_snapshot_count = 0;

    integer pc_sample_count;
    initial pc_sample_count = 0;

    integer pc220_stall_count;
    initial pc220_stall_count = 0;

    integer ws_done_edges;
    initial ws_done_edges = 0;

    integer loader_done_edges;
    initial loader_done_edges = 0;

    always @(posedge uut.sys_clk) begin
        heartbeat_count = heartbeat_count + 1;
        if (heartbeat_count[7:0] == 8'h00) begin
            if (verbose_heartbeat) begin
                $display("SIM heartbeat: t=%0t PC=%08x dbus_cyc=%b dbus_stb=%b dbus_ack=%b grant=%0d req=%03b dma_state=%0d dma_off=%0d fifo=%0d loader_busy=%b loader_done=%b dma_done=%b",
                    $time,
                    uut.VexRiscv.lastStagePc,
                    uut.basesoc_dbus_cyc,
                    uut.basesoc_dbus_stb,
                    uut.basesoc_dbus_ack,
                    uut.socbushandler_grant,
                    uut.socbushandler_request,
                    uut.subfragments_wishbonedmareader_state,
                    uut.disp0_dma_offset1,
                    uut.disp0_dma_fifo_level,
                    uut.disp0_busy,
                    uut.disp0_done,
                    uut.disp0_dma_done);
            end
        end

        pc_sample_count = pc_sample_count + 1;
        if (pc_sample_count[15:0] == 16'h0000) begin
            $display("PC sample: fetchPc=%08x decode=%08x execute=%08x memory=%08x writeBack=%08x last=%08x t=%0t",
                uut.VexRiscv.IBusCachedPlugin_fetchPc_pcReg,
                uut.VexRiscv.decode_PC,
                uut.VexRiscv.execute_PC,
                uut.VexRiscv.memory_PC,
                uut.VexRiscv.writeBack_PC,
                uut.VexRiscv.lastStagePc,
                $time);
        end

        if (uut.VexRiscv.lastStagePc == 32'h00000220) begin
            pc220_stall_count = pc220_stall_count + 1;
            if (pc220_stall_count[15:0] == 16'h0000) begin
                $display("STALL@PC220(loader_done poll): dbus cyc=%b stb=%b ack=%b adr=%08x dat_r=%08x grant=%0d req=%03b slave_sel=%04b shared_ack=%b if0 cyc=%b stb=%b ack=%b if1_re=%b csr_disp0_sel=%b loader_done=%b loader_busy=%b dma_done=%b dma_state=%0d dma_off=%0d dma_len_words=%0d dma_ack=%b dma_adr=%08x fifo_level=%0d sink_ready=%b source_valid=%b source_ready=%b loader_we=%b loader_addr=%0d dma_sink_last=%b dma_source_last=%b loader_last=%b t=%0t",
                    uut.basesoc_dbus_cyc,
                    uut.basesoc_dbus_stb,
                    uut.basesoc_dbus_ack,
                    uut.basesoc_dbus_adr,
                    uut.basesoc_dbus_dat_r,
                    uut.socbushandler_grant,
                    uut.socbushandler_request,
                    uut.socbushandler_slave_sel,
                    uut.socbushandler_shared_ack,
                    uut.interface0_cyc,
                    uut.interface0_stb,
                    uut.interface0_ack,
                    uut.interface1_re,
                    uut.csr_bankarray_csrbank1_sel,
                    uut.disp0_done,
                    uut.disp0_busy,
                    uut.disp0_dma_done,
                    uut.subfragments_wishbonedmareader_state,
                    uut.disp0_dma_offset1,
                    uut.disp0_dma_length1,
                    uut.ws2812_dma_bus_ack,
                    uut.ws2812_dma_bus_adr,
                    uut.disp0_dma_fifo_level,
                    uut.disp0_sink_ready,
                    uut.disp0_dma_source_source_valid,
                    uut.disp0_dma_source_source_ready,
                    uut.disp0_we,
                    uut.disp0_w_address,
                    uut.disp0_dma_sink_sink_last,
                    uut.disp0_dma_source_source_last,
                    uut.disp0_sink_last,
                    $time);
            end
        end else begin
            pc220_stall_count = 0;
        end
    end

    always @(posedge uut.disp0_we) begin
        writes = writes + 1;
        cycles_since_write = 0;
        if (verbose_dma_events) begin
            $display("DMA->WS2812 write %0d: addr=%0d data=%06x stream=%08x t=%0t",
                writes,
                uut.disp0_w_address,
                uut.disp0_w_data,
                uut.disp0_sink_payload_data,
                $time);
        end
        if (finish_on_expected_writes && (writes == expected_dma_writes)) begin
            // led_mem_dual writes on negedge, so wait a few cycles before
            // printing memory and finishing.
            #(tck*4);
            $display("Expected DMA->WS2812 writes reached: writes=%0d", writes);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
            $finish;
        end
    end

    always @(negedge uut.ws2812_periph.mem0.clk) begin
        if (uut.ws2812_periph.mem0.we_a) begin
            // led_mem_dual commits MEM[w_address] on this same negedge. Wait
            // one delta/timestep so the array update and its alias wires are
            // present in the VCD, then flush. Flushing at loader_we is too
            // early because loader_we rises before this negedge write commit.
            #1;
            if (verbose_dma_events) begin
                $display("WS2812 MEM commit: addr=%0d data=%06x MEM[%0d]=%06x dma_off=%0d fifo=%0d loader_done=%b t=%0t",
                    uut.ws2812_periph.mem0.w_address,
                    uut.ws2812_periph.mem0.w_data,
                    uut.ws2812_periph.mem0.w_address,
                    uut.ws2812_periph.mem0.MEM[uut.ws2812_periph.mem0.w_address],
                    uut.disp0_dma_offset1,
                    uut.disp0_dma_fifo_level,
                    uut.disp0_done,
                    $time);
            end
            // Force a complete snapshot of all currently dumped variables at
            // each committed LED RAM write. This makes GTKWave/VCD inspection
            // easier around sparse events: the file contains the current state
            // of PC, DMA, stream, loader and mem aliases at each write point,
            // not only variables that changed since the previous timestamp.
            if (verbose_dma_events) begin
                $dumpall;
                $dumpflush;
            end
        end
    end

    always @(posedge uut.sys_clk) begin
        if (uut.ws2812_dma_bus_cyc && uut.ws2812_dma_bus_stb && uut.ws2812_dma_bus_ack) begin
            #1;
            if (verbose_dma_events) begin
                $display("DMA ACK: adr=%08x dat_r=%08x dma_off=%0d fifo=%0d dma_sink_last=%b fifo_in_last=%b fifo_out_last=%b src_v/r/l=%b/%b/%b loader_v/r/l=%b/%b/%b loader_addr=%0d writes=%0d t=%0t",
                    uut.ws2812_dma_bus_adr,
                    uut.ws2812_dma_bus_dat_r,
                    uut.disp0_dma_offset1,
                    uut.disp0_dma_fifo_level,
                    uut.disp0_dma_sink_sink_last,
                    uut.disp0_dma_fifo_sink_last,
                    uut.disp0_dma_fifo_source_last,
                    uut.disp0_dma_source_source_valid,
                    uut.disp0_dma_source_source_ready,
                    uut.disp0_dma_source_source_last,
                    uut.disp0_sink_valid,
                    uut.disp0_sink_ready,
                    uut.disp0_sink_last,
                    uut.disp0_w_address,
                    writes,
                    $time);
            end
            if (verbose_dma_events) begin
                $dumpall;
                $dumpflush;
            end
        end
    end

    always @(posedge uut.sys_clk) begin
        if (uut.disp0_busy || uut.disp0_dma_enable_storage) begin
            dump_snapshot_count = dump_snapshot_count + 1;
            if (dump_snapshot_count[11:0] == 12'h000) begin
                // Sparse keep-alive snapshot only. Dense snapshots every
                // sys_clk made vvp/VCD generation extremely slow for large
                // transfers such as N_LEDS=256. Detailed snapshots are already
                // produced on DMA ACK and real MEM commit events.
                if (enable_vcd) begin
                    $dumpall;
                    $dumpflush;
                end
            end
        end else begin
            dump_snapshot_count = 0;
        end
    end

    always @(posedge uut.sys_clk) begin
        if (enable_loader_watchdog && uut.disp0_busy && !uut.disp0_done && (writes != 0)) begin
            cycles_since_write = cycles_since_write + 1;
            if (cycles_since_write == 1024) begin
                $display("WS2812 loader watchdog: no new writes after %0d writes at t=%0t", writes, $time);
                $display("PC=%08x dma_state=%0d dma_off=%0d dma_len_words=%0d dma_done=%b fifo=%0d", 
                    uut.VexRiscv.lastStagePc,
                    uut.subfragments_wishbonedmareader_state,
                    uut.disp0_dma_offset1,
                    uut.disp0_dma_length1,
                    uut.disp0_dma_done,
                    uut.disp0_dma_fifo_level);
                $display("DMA bus: cyc=%b stb=%b ack=%b adr=%08x dat_r=%08x grant=%0d req=%03b shared_ack=%b ram_ack=%b", 
                    uut.ws2812_dma_bus_cyc,
                    uut.ws2812_dma_bus_stb,
                    uut.ws2812_dma_bus_ack,
                    uut.ws2812_dma_bus_adr,
                    uut.ws2812_dma_bus_dat_r,
                    uut.socbushandler_grant,
                    uut.socbushandler_request,
                    uut.socbushandler_shared_ack,
                    uut.basesoc_ram_bus_ram_bus_ack);
                $display("Stream: dma_sink v/r=%b/%b dma_source v/r=%b/%b loader_sink v/r=%b/%b loader_busy=%b loader_done=%b loader_addr=%0d loader_we=%b", 
                    uut.disp0_dma_sink_sink_valid,
                    uut.disp0_dma_sink_sink_ready,
                    uut.disp0_dma_source_source_valid,
                    uut.disp0_dma_source_source_ready,
                    uut.disp0_sink_valid,
                    uut.disp0_sink_ready,
                    uut.disp0_busy,
                    uut.disp0_done,
                    uut.disp0_w_address,
                    uut.disp0_we);
                for (idx = 0; idx < 8; idx = idx + 1)
                    $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
                for (idx = 0; idx < 8; idx = idx + 1)
                    $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
                $finish;
            end
        end else begin
            cycles_since_write = 0;
        end
    end

    always @(posedge uut.disp0_done) begin
        loader_done_edges = loader_done_edges + 1;
        $display("LOADER DONE EDGE: loader_done=%b dma_done=%b writes=%0d dma_off=%0d dma_len_words=%0d dma_adr=%08x fifo=%0d dma_sink_last=%b dma_source_last=%b loader_last=%b t=%0t",
            uut.disp0_done,
            uut.disp0_dma_done,
            writes,
            uut.disp0_dma_offset1,
            uut.disp0_dma_length1,
            uut.ws2812_dma_bus_adr,
            uut.disp0_dma_fifo_level,
            uut.disp0_dma_sink_sink_last,
            uut.disp0_dma_source_source_last,
            uut.disp0_sink_last,
            $time);
        if (finish_on_loader_done) begin
            // La RAM led_mem_dual escribe en negedge; esperar unos ciclos para
            // que la última escritura y las señales de estado queden visibles
            // en el VCD antes del $finish.
            #(tck*4);
            $display("Loader completed: observed DMA->WS2812 writes=%0d", writes);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
            $finish;
        end
    end

    always @(posedge uut.ws2812_periph.done) begin
        ws_done_edges = ws_done_edges + 1;
        $display("WS2812 DONE EDGE: ws_done_edges=%0d loader_done_edges=%0d loader_done=%b dma_done=%b writes=%0d ws_addr=%0d dout=%b mem0=%06x mem63=%06x t=%0t",
            ws_done_edges,
            loader_done_edges,
            uut.disp0_done,
            uut.disp0_dma_done,
            writes,
            uut.ws2812_periph.address,
            uut.ws2812_periph.dout,
            uut.ws2812_periph.mem0.MEM[0],
            uut.ws2812_periph.mem0.MEM[63],
            $time);
        if (finish_on_ws_done && (ws_done_edges >= finish_after_ws_done_edges)) begin
            #(tck*4);
            $display("WS2812 completed: observed DMA->WS2812 writes=%0d loader_done_edges=%0d ws_done_edges=%0d",
                writes,
                loader_done_edges,
                ws_done_edges);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
            $finish;
        end
    end

    always @(posedge uut.sys_clk) begin
        if (finish_on_both_done && uut.disp0_done && uut.disp0_dma_done) begin
            #(tck*4);
            $display("BOTH DONE: loader_done=%b dma_done=%b writes=%0d dma_off=%0d dma_len_words=%0d t=%0t",
                uut.disp0_done,
                uut.disp0_dma_done,
                writes,
                uut.disp0_dma_offset1,
                uut.disp0_dma_length1,
                $time);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
            for (idx = 0; idx < 8; idx = idx + 1)
                $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
            $finish;
        end
    end

    always @(posedge uut.sys_clk) begin
        if (verbose_dma_bus && uut.ws2812_dma_bus_cyc && uut.ws2812_dma_bus_stb) begin
            $display("DMA SRAM bus: grant=%0d adr=%08x sram_adr=%0d ack=%b dat_r=%08x offset=%0d len_words=%0d state=%0d fifo_level=%0d t=%0t",
                uut.socbushandler_grant,
                uut.ws2812_dma_bus_adr,
                uut.basesoc_ram_adr,
                uut.ws2812_dma_bus_ack,
                uut.ws2812_dma_bus_dat_r,
                uut.disp0_dma_offset1,
                uut.disp0_dma_length1,
                uut.subfragments_wishbonedmareader_state,
                uut.disp0_dma_fifo_level,
                $time);
        end
    end

    initial begin
        #(tck*sim_cycles);
        $display("Simulation stop: observed DMA->WS2812 writes=%0d ws_done_edges=%0d ws_done=%b loader_done=%b dma_done=%b ws_addr=%0d",
            writes,
            ws_done_edges,
            uut.ws2812_periph.done,
            uut.disp0_done,
            uut.disp0_dma_done,
            uut.ws2812_periph.address);
        for (idx = 0; idx < 8; idx = idx + 1)
            $display("SRAM[%0d]=%08x", idx, uut.sram[idx]);
        for (idx = 0; idx < 8; idx = idx + 1)
            $display("MEM[%0d]=%06x", idx, uut.ws2812_periph.mem0.MEM[idx]);
        $finish;
    end
endmodule
