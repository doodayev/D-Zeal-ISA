// memory.sv for ZEAL

module memory #(
    parameter WORDS = 128,
    parameter mem_init = ""
) (
    input logic clk,
    input logic [63:0] address, //We are doing 64-bit memory addresses and data!
    input logic [63:0] write_data,
    input logic [7:0] byte_enable,
    input logic write_enable,
    input logic rst_n,

    output logic [63:0] read_data
);

/*
* This memory is byte addressed
* but we have currently no support for mis-aligned writes nor reads.
*/

reg [63:0] mem [0:WORDS-1]; // Memory array of words (64-bits)

initial begin
    if (mem_init != "") begin
        $readmemh(mem_init, mem);
    end
end

/* verilator lint_off WIDTHTRUNC */
always @(posedge clk) begin
    // reset logic
    if (rst_n == 1'b0) begin
        for (int i=0; i < WORDS; i++) begin
            mem[i] <= 64'b0;
        end
    end
    else if (write_enable) begin
        if (address[2:0] != 3'b000) begin
            $display("Misaligned write at address %h", address);
        end else begin
            // use byte-enable to selectively write bytes
            for (int i= 0; i< 8; i++) begin
                if (byte_enable[i]) begin
                    mem[address[63:3]][(i*8)+:8] <= write_data[(i*8)+:8];
                end
            end
        end
    end
end

// Read logic
always_comb begin
    //here, address [63:3] is the word index
    read_data = mem[address[63:3]];
end
/* verilator lint_on WIDTHTRUNC */
endmodule
