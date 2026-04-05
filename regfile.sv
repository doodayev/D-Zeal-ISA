// regfile.sv

module regfile (
    // basic signals
    input logic clk,
    input logic rst_n,

    // Reads
    input logic [7:0] address1,
    input logic [7:0] address2,
    output logic [63:0] read_data1,
    output logic [63:0] read_data2,

    // Writes
    input logic write_enable,
    input logic [63:0] write_data,
    input logic [7:0] address3
);

// 64-bit register, 256 of them (addressed with 8 bits)
reg [63:0] registers [0:255];

// Write logic
always @(posedge clk) begin
    // reset support, init to 0
    if(rst_n == 1'b0) begin
        for(int i=0; i<256; i++) begin
            registers[i] <= 64'b0;
        end
    end
    // Write, except on 0, reserved for a zero constant according to ZEAL specs
    else if(write_enable == 1'b1 && address3 != 0) begin
        registers[address3] <= write_data;
    end
end

// Read logic, async
always_comb begin : readLogic
    read_data1 = registers[address1];
    read_data2 = registers[address2];
end

endmodule
