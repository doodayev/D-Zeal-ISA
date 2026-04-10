// reader.sv

module reader(
    input logic [63:0] mem_data,
    input logic [7:0] byteMask,
    input logic [3:0] f4,

    output logic [63:0] writeBack,
    output logic valid);

logic sign_extend;
assign sign_extend = ~f4[3];

logic [63:0] masked_data; // just a mask applied
logic [63:0] raw_data;    // Data shifted according to instruction
                          // and then mem_data is the final output with sign extension

always_comb begin: mask_apply
    for (int i=0; i<8; i++) begin
        if (byteMask[i]) begin
            masked_data[(i*8)+:8] = mem_data [(i*8)+:8];
        end else begin
            masked_data[(i*8)+:8] = 8'h00;
        end
    end
end

always_comb begin : shift_data
    case (f4)
        4'b0100 : raw_data = masked_data; // masked data is the WORLD (full word) in that case

        4'b0000, 4'b1000: begin // LoadByte and LoadByteUnsigned
            case (byteMask)
                8'b00000001: raw_data = masked_data;
                8'b00000010: raw_data = masked_data >> 8;
                8'b00000100: raw_data = masked_data >> 16;
                8'b00001000: raw_data = masked_data >> 24;
                8'b00010000: raw_data = masked_data >> 32;
                8'b00100000: raw_data = masked_data >> 40;
                8'b01000000: raw_data = masked_data >> 48;
                8'b10000000: raw_data = masked_data >> 56;
                default: raw_data = 64'b0;
            endcase
        end

        4'b0001, 4'b1001: begin // (2bytes, quarter-words)
            case (byteMask)
                8'b00000011: raw_data = masked_data;
                8'b00001100: raw_data = masked_data >> 16;
                8'b00110000: raw_data = masked_data >> 32;
                8'b11000000: raw_data = masked_data >> 48;
                default: raw_data = 64'b0;
            endcase
        end

        4'b0010, 4'b1010: begin // (4bytes, half-words)
            case (byteMask)
                8'b00001111: raw_data = masked_data;
                8'b11110000: raw_data = masked_data >> 32;
                default: raw_data = 64'b0;
            endcase
        end

        default: raw_data = 64'b0;
    endcase
end

always_comb begin: sign_extend_logic
    case (f4)
    // Load 8byte
    4'b0100 : writeBack = raw_data;
    // Load byte
    4'b0000, 4'b1000: writeBack = sign_extend ? {{56{raw_data[7]}},raw_data[7:0]} : raw_data;
    // Load 2byte
    4'b0001, 4'b1001: writeBack = sign_extend ? {{48{raw_data[15]}},raw_data[15:0]} : raw_data;
    // Load 4byte
    4'b0010, 4'b1010: writeBack = sign_extend ? {{32{raw_data[31]}},raw_data[31:0]} : raw_data;

    default: writeBack = 64'b0; // Added missing default
    endcase

    valid = |byteMask;
end

endmodule
