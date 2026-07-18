module cpu_core (
    input  clk,
    input  rst_n,
    input  i_step,
    input  [4:0] opcode,
    input  [7:0] data_in,
    input        sensor_in,
    output reg [7:0] pc,
    output reg [7:0] acc,
    output reg [7:0] port16_pattern
);
    wire [7:0] alu_out;
    wire alu_zero;
    reg  z_flag;

    alu_8bit u_alu (
        .a_reg(acc),
        .data_in(data_in),
        .opcode(opcode),
        .out(alu_out),
        .zero(alu_zero)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc             <= 8'h00;
            acc            <= 8'h00;
            z_flag         <= 1'b0;
            port16_pattern <= 8'h00;
        end else if (i_step) begin
            pc <= pc + 1'b1;
            case (opcode)
                5'h01, 5'h02, 5'h03, 5'h04, 5'h05, 5'h06,
                5'h07, 5'h08, 5'h09, 5'h0A, 5'h0B, 5'h0C: begin
                    acc    <= alu_out;
                    z_flag <= alu_zero;
                end
                5'h0D: pc <= data_in;
                5'h0E: if (z_flag) pc <= data_in;
                5'h0F: if (!z_flag) pc <= data_in;

                5'h10: begin
                    acc    <= {7'b0, sensor_in};
                    z_flag <= !sensor_in;
                end

                5'h12: port16_pattern <= data_in;

                default: ;
            endcase
        end
    end
endmodule