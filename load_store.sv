// load_store.sv
module load_store (
    input logic [63:0] alu_result_address,
    input logic [3:0] f4,
    input logic [63:0] reg_read,
    output logic [7:0] byte_enable,
    output logic [63:0] data
);

logic [2:0] offset;

assign offset = alu_result_address[2:0];

always_comb begin
    case (f4)
        4'b0000, 4'b1000: begin // StoreByte or StoreSquad or Steigth (Store+Eighth)
            case (offset)
                3'b000: begin
                    byte_enable = 8'b00000001;
                    data = (reg_read & 64'h00000000000000FF);
                end
                3'b001: begin
                    byte_enable = 8'b00000010;
                    data = (reg_read & 64'h00000000000000FF) << 8;
                end
                3'b010: begin
                    byte_enable = 8'b00000100;
                    data = (reg_read & 64'h00000000000000FF) << 16;
                end
                3'b011: begin
                    byte_enable = 8'b00001000;
                    data = (reg_read & 64'h00000000000000FF) << 24;
                end
                3'b100: begin
                    byte_enable = 8'b00010000;
                    data = (reg_read & 64'h00000000000000FF) << 32;
                end
                3'b101: begin
                    byte_enable = 8'b00100000;
                    data = (reg_read & 64'h00000000000000FF) << 40;
                end
                3'b110: begin
                    byte_enable = 8'b01000000;
                    data = (reg_read & 64'h00000000000000FF) << 48;
                end
                3'b111: begin
                    byte_enable = 8'b10000000;
                    data = (reg_read & 64'h00000000000000FF) << 56;
                end
                default: byte_enable = 8'b00000000;
            endcase
        end
        4'b0001, 4'b1001: begin // StoreQuart or Squart (Store+quart) or StoreBrigade or Store2pac (2 byte... 2pac idk)
            case (offset)
                3'b000: begin
                    byte_enable = 8'b00000011;
                    data = (reg_read & 64'h000000000000FFFF);
                end
                3'b010: begin
                    byte_enable = 8'b00001100;
                    data = (reg_read & 64'h000000000000FFFF) << 16;
                end
                3'b100: begin
                    byte_enable = 8'b00110000;
                    data = (reg_read & 64'h000000000000FFFF) << 32;
                end
                3'b110: begin
                    byte_enable = 8'b11000000;
                    data = (reg_read & 64'h000000000000FFFF) << 48;
                end
                default: byte_enable = 8'b00000000;
            endcase
        end
        4'b0010, 4'b1010: begin // StoreChud or StoreChina or Stalf (Store+half)
            case (offset)
                3'b000: begin
                    byte_enable = 8'b00001111;
                    data = (reg_read & 64'h00000000FFFFFFFF);
                end
                3'b100: begin
                    byte_enable = 8'b11110000;
                    data = (reg_read & 64'h00000000FFFFFFFF) << 32;
                end
                default: byte_enable = 8'b00000000;
           endcase
        end
        4'b0100: begin // StoreWorld (yeah THE WORLD) or StoreFull
            byte_enable = (offset == 3'b000) ? 8'b11111111 : 8'b00000000;
            data = reg_read;
        end

        default: begin
            byte_enable = 8'b00000000; // No operation for unsupported types
        end
    endcase
end

endmodule
