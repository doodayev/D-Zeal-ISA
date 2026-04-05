module alu (
    // IN
    input logic [3:0] alu_control,
    input logic [63:0] src1,
    input logic [63:0] src2,
    // OUT
    output logic [63:0] alu_result,
    output logic zero,
    output logic last_bit
);

wire [5:0] shamt = src2[5:0]; //2^6 = 64 so shift up to 64 binary places

always_comb begin
    case (alu_control)
        // ADD STUFF
        4'b0000: alu_result = src1 + src2;
        // AND STUFF
        4'b0001: alu_result = src1 & src2;
        // OR
        4'b0010: alu_result = src1 | src2;
        // SUB (rs1- rs2)
        4'b0011: alu_result = src1 + (~src2 + 1'b1); //Two's compliment
        // SLT (Set less than) (src1 < src2)
        4'b0100: alu_result = {63'b0, $signed(src1) < $signed(src2)};
        // SLTU (Set less than unsigned) (src1 < src2)
        4'b0101: alu_result = {63'b0, src1 < src2};
        // XOR
        4'b0110: alu_result = src1 ^ src2;
        // SLL
        4'b0111: alu_result = src1 << shamt;
        // SRL
        4'b1000: alu_result = src1 >> shamt;
        // SRA
        4'b1001: alu_result = $signed(src1) >>> shamt; //an extra > makes it signed? Yeah it does lol
        // NE (Not Equal) I might have to expand the ALU beyond 4-bits.
        4'b1010: alu_result = {63'b0, !(src1 == src2)};
        // GLT (Set greater than) (src1 > src2)
        4'b1011: alu_result = {63'b0, $signed(src1) > $signed(src2)};
        // GLTU (Set greater than unsigned)
        4'b1100: alu_result = {63'b0, src1 > src2};
        // NON IMPLEMENTED STUFF
        default: alu_result = 64'b0;
    endcase
end

assign zero = alu_result == 64'b0;
assign last_bit = alu_result[0];

endmodule
