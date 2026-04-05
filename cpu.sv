// cpu.sv

module cpu (
input logic clk,
input logic rst_n
);

/**
* PROGRAM COUNTER
*/

reg [63:0] pc;
logic [63:0] pc_next;
logic [63:0] pc_plus_second_add;
logic [63:0] pc_plus_eight;
// assign pc_plus_second_add = pc + immediate; formerly pc_target
assign pc_plus_eight = pc + 8;

always_comb begin:pcSelect
    case (pc_source)
        1'b0 : pc_next = pc_plus_eight; // pc + 8
        1'b1: pc_next = pc_plus_second_add;
    endcase
end

always_comb begin : second_add_select
    case (second_add_source)
        2'b00 : pc_plus_second_add = pc + immediate;
        2'b01 : pc_plus_second_add = immediate;
        2'b10 : pc_plus_second_add = read_reg1 + immediate;
        2'b11 : pc_plus_second_add = pc + immediate; //placeholder default
    endcase
end

always @(posedge clk) begin
    if(rst_n == 0) begin
        pc <= 64'b0;
    end
    else begin
        pc <= pc_next;
    end
end





/**
* INSTRUCTION MEMORY
*/

// Acts as a ROM
wire [63:0] instruction;

memory #(
    .mem_init("./test_imemory.hex")
)
instruction_memory (
//Memory inputs
.clk(clk),
.address(pc),
.write_data(64'b0),
.write_enable(1'b0),
.rst_n(1'b1),
.byte_enable(8'b0),

// Memory outputs
.read_data(instruction)
);


/**
* CONTROL
*/

// Intercepts instruction data, generates control signals accordingly in control unit
logic [15:0] op;
assign op = instruction[63:48];
//63, 62, 61, 60
//59, 58, 57, 56
//55, 54, 53, 52
//51, 50, 49, 48
logic [3:0] f4;
assign f4 = instruction [51:48];
wire alu_zero;
// out of control unit
wire [3:0] alu_control;
wire [2:0] imm_source;
wire mem_write;
wire reg_write;
wire alu_last_bit;

// out muxes wires
wire alu_source;
wire [1:0] write_back_source;
wire pc_source;
wire branch_inst;
wire itype_src2_rs1;
wire [1:0] second_add_source;

control control_unit(
.op(op),
.func4(f4),
.func8(8'b0),
.alu_zero(alu_zero),
.alu_last_bit(alu_last_bit),

//OUT
.alu_control(alu_control),
.imm_source(imm_source),
.mem_write(mem_write),
.reg_write(reg_write),
// muxes out
.alu_source(alu_source),
.write_back_source(write_back_source),
.pc_source(pc_source),
.branch_inst(branch_inst),
.itype_src2_rs1(itype_src2_rs1),
.second_add_source(second_add_source)
);




/**
* REGFILE
*/

logic [7:0] source_reg1;
assign source_reg1 = instruction[31:24];
logic [7:0] source_reg2;
assign source_reg2 = instruction[39:32];
logic [7:0] dest_reg;
assign dest_reg = instruction[47:40];
wire [63:0] read_reg1;
wire [63:0] read_reg2;
logic write_back_valid;

logic [7:0] rs1_addr; // ADDED TO DEAL WITH CHANGING DESTINATION TO R1 FOR BRANCH INSTRUCTIONS
//assign rs1_addr = control_unit.branch_inst ? dest_reg : source_reg1; // BRANCH SHENANIGANS
always_comb begin
    if (control_unit.branch_inst)
        rs1_addr = dest_reg;                // for branches
    else if (control_unit.itype_src2_rs1)
        rs1_addr = source_reg2;             // for ADDI
    else
        rs1_addr = source_reg1;             // for all others
end

logic [63:0] write_back_data;

logic[63:0] reader_data;
logic reader_valid;

always_comb begin: write_back_source_select
    case (write_back_source)
        2'b00: begin
            write_back_data = alu_result;
            write_back_valid = 1'b1;
        end
        2'b01: begin
            write_back_data = reader_data;
            write_back_valid = reader_valid;
        end
        2'b10: begin
            write_back_data = pc_plus_eight;
            write_back_valid = 1'b1;
        end
        2'b11: begin
            write_back_data = pc_plus_second_add;
            write_back_valid = 1'b1;
        end
    endcase
end


regfile regfile(
    // basic signals
    .clk(clk),
    .rst_n(rst_n),

    //Read In
    .address1(rs1_addr), // changed from source_reg1 to rs1_addr for branch shenanigans
    .address2(source_reg2),
    //Read out
    .read_data1(read_reg1),
    .read_data2(read_reg2),

    //Write In
    .write_enable(reg_write),
    .write_data(write_back_data),
    .address3(dest_reg)
);

/**
*SIGN EXTEND
*/
logic [31:0] raw_imm;
assign raw_imm = instruction[31:0];
wire [63:0] immediate;

signext sign_extender(
    .raw_src(raw_imm),
    .imm_source(imm_source),
    .immediate(immediate)
);

/**
*ALU
*/
wire [63:0] alu_result;
logic [63:0] alu_src2;

always_comb begin: alu_source_select
    case (alu_source)
        1'b1: alu_src2 = immediate;
        default: alu_src2 = read_reg2;
    endcase
end

alu alu_inst(
    .alu_control(alu_control),
    .src1(read_reg1),
    .src2(alu_src2),
    .alu_result(alu_result),
    .zero(alu_zero),
    .last_bit(alu_last_bit)
);

/**
* LOAD/STORE DECODER
*/

wire [7:0] mem_byte_enable;
wire [63:0] store_data;

load_store ls_decode(
    .alu_result_address(alu_result),
    .reg_read(read_reg2),
    .f4(f4),
    .byte_enable(mem_byte_enable),
    .data(store_data)
);



/**
* DATA MEMORY
*/
wire [63:0] mem_read;
wire mem_read_valid;

memory #(
    .mem_init("./test_dmemory.hex")
)
data_memory (
 // Memory inputs
 .clk(clk),
 .address({alu_result[63:3], 3'b000}),
 .write_data(store_data),
 .write_enable(mem_write),
 .byte_enable(mem_byte_enable),
 .rst_n(1'b1),

 //Memory outputs
 .read_data(mem_read)
 );

/**
* READER
*/


reader reader_inst(
    .mem_data(mem_read),
    .byteMask(mem_byte_enable),
    .f4(f4),
    .writeBack(reader_data),
    .valid(reader_valid)
);

 endmodule

