module ctrl_ws_arr (
    input clk,
    input reset,
    input init_m,
    input done_led,
    input z,

    output reg init_led,
    output reg rst,
    output reg inc,
    output reg done
);

 parameter START      = 3'b000;
 parameter START_SEND = 3'b001;
 parameter SEND_LED   = 3'b010;
 parameter WAIT_TX    = 3'b011;
 parameter INC        = 3'b100;
 parameter CHECK_END  = 3'b101;
 parameter END_SEND   = 3'b110;
 parameter LOAD_WAIT  = 3'b111;

reg [2:0] state;

always @(posedge clk ) begin
    if (reset) begin
        state = START;
    end else begin
        case (state)
            START:
                if(init_m)
                    state = LOAD_WAIT;
                else
                    state = START;
            START_SEND:
                state = SEND_LED;
            SEND_LED:
                state = WAIT_TX;
            WAIT_TX:
                if(done_led)
                    state = CHECK_END;
                else
                    state = WAIT_TX;
            INC:
                state = LOAD_WAIT;
            LOAD_WAIT:
                state = START_SEND;
            CHECK_END:
                if(z)
                    state = END_SEND;
                else
                    state = INC;
            END_SEND:
                if(init_m)
                    state = START;
                else 
                    state = END_SEND;
            default:
                state = START;

        endcase
    end
end

always @(* ) begin
    case (state)
        START: begin
            init_led <= 0;
            rst      <= 1;
            inc      <= 0;
            done     <= 0;
        end
        START_SEND: begin
            init_led <= 1;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end
        SEND_LED: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end
        WAIT_TX: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end
        INC: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 1;
            done     <= 0;
        end
        LOAD_WAIT: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end
        CHECK_END: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end
        END_SEND: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 1;
        end
        default: begin
            init_led <= 0;
            rst      <= 0;
            inc      <= 0;
            done     <= 0;
        end

    endcase
end

`ifdef BENCH
reg [8*40:1] state_name;
always @(*) begin
  case(state)
    START      : state_name = "START";
    START_SEND : state_name = "CHK_SEL";
    SEND_LED   : state_name = "SEND_BIT";
    WAIT_TX    : state_name = "WAIT_TX";
    INC        : state_name = "SHUFT";
    CHECK_END  : state_name = "CHECK_END";
    END_SEND   : state_name = "END_SEND";
    LOAD_WAIT  : state_name = "LOAD_WAIT";
  endcase
end
`endif
endmodule
