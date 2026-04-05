module control (
//IN
input logic [15:0] op,
input logic [3:0] func4, //4-bit func4
input logic [7:0] func8, //we actually have 24-bits available but for now just use 8
//we use 8 because i've got no clue what I'd need that many more for and that's up
//to others to figure out. We already have 16-bit opcodes
input logic alu_zero,
input logic alu_last_bit,

//OUT
output logic [3:0] alu_control,
output logic [2:0] imm_source,
output logic mem_write,
output logic reg_write,
output logic alu_source,
output logic [1:0] write_back_source,
output logic pc_source,
output logic branch_inst, // ADDED TO DEAL WITH CHANGING DESTINATION TO R1 FOR BRANCH INSTRUCTIONS
output logic itype_src2_rs1, // Deal with I-type so ALU can use RS2
output logic [1:0] second_add_source
);

/**
* MAIN DECODER
*/

logic [1:0] alu_op;
logic branch;
logic jump;

always_comb begin
    case (op)
    //LoadSquad, LoadBrigade, LoadChud, LoadWorld, and then their signed equivalents
    //16'b0000000000010000: begin //I decided to put the "load word" opcode as such because all zeros should be for the first ALU
    16'hB010, 16'hB011, 16'hB012, 16'hB014, 16'hB019, 16'hB01A, 16'hB01B, 16'hB01D: begin
        reg_write = 1'b1;
        imm_source = 3'b000;
        mem_write = 1'b0;
        alu_op = 2'b00;
        alu_source = 1'b1; // imm
        write_back_source = 2'b01; //memory_read
        branch = 1'b0;
        jump = 1'b0;
        itype_src2_rs1 = 1'b0;
        second_add_source = 2'b00;
    end
    // S-Type C010 = StoreSquadron, C011 = StoreBrigade, C012 = StoreChina, C014 = StoreWorld
    16'hC010, 16'hC011, 16'hC012, 16'hC014: begin
      reg_write = 1'b0;
      imm_source = 3'b001;
      mem_write = 1'b1;
      alu_op = 2'b00;
      alu_source = 1'b1; // imm
      write_back_source = 2'b00;
      branch = 1'b0;
      jump = 1'b0;
      itype_src2_rs1 = 1'b0;
      second_add_source = 2'b00;
    end
    // R- Type (ADD, AND, OR, SUB, SLT, SLTU, XOR, SLL, SRL, SRAI, NE, SGT)
    16'hA000, 16'hA001, 16'hA002, 16'hA003, 16'hA004, 16'hA005, 16'hA006, 16'hA007, 16'hA008, 16'hA009, 16'hA00A, 16'hA00B, 16'hA00C : begin
      reg_write = 1'b1;
      mem_write = 1'b0;
      alu_op = 2'b10;
      alu_source = 1'b0; //reg2
      write_back_source = 2'b00; //alu_result
      branch = 1'b0;
      jump = 1'b0;
      itype_src2_rs1 = 1'b0;
      imm_source = 3'b000;
      second_add_source = 2'b00;
    end
    // B-type (BEQ, BLT,BNE, BGT)
    16'hD003, 16'hD004, 16'hD005, 16'hD00A, 16'hD00B, 16'hD00C: begin
      reg_write = 1'b0;
      imm_source = 3'b010;
      alu_op = 2'b01;
      alu_source = 1'b0;
      mem_write = 1'b0;
      branch = 1'b1;
      jump = 1'b0;
      write_back_source = 2'b00;
      itype_src2_rs1 = 1'b0;
      second_add_source = 2'b00;
    end
    // J-type (JUMP)
    16'hE010: begin
      reg_write = 1'b1;
      imm_source = 3'b011;
      alu_source = 1'b0;
      mem_write = 1'b0;
      write_back_source = 2'b10;
      branch = 1'b0;
      jump = 1'b1;
      itype_src2_rs1 = 1'b0;
      second_add_source = 2'b00;
    end
    // JALR (Jump and Link), this is a weird one. Encoded with "B" because it's encoded like
    // an I-type. "E" to designate a "subtype" of being a jump.
    16'hBE00: begin
      reg_write = 1'b1;
      imm_source = 3'b000;
      alu_source = 1'b0; // I think this is right???
      mem_write = 1'b0;
      write_back_source = 2'b10;
      branch = 1'b0;
      jump = 1'b1;
      second_add_source = 2'b10;
      itype_src2_rs1 = 1'b1;
      alu_op = 2'b00;
    end
    // ALU I-type (addi, andi, ori, subi, slti, sltiu, xori, slli, srli, srai, nei, sgti, sgtiu)
    16'hB000, 16'hB001, 16'hB002, 16'hB003, 16'hB004, 16'hB005, 16'hB006, 16'hB007, 16'hB008, 16'hB009, 16'hB00A, 16'hB00B, 16'hB00C: begin
      reg_write = 1'b1;
      imm_source = 3'b000;
      alu_source = 1'b1; //imm
      mem_write = 1'b0;
      alu_op = 2'b10;
      write_back_source = 2'b00; //alu_result
      branch = 1'b0;
      jump = 1'b0;
      itype_src2_rs1 = 1'b1;
      second_add_source = 2'b00;
    end

    // U-type
    16'hF010, 16'hF011: begin
      imm_source = 3'b100;
      mem_write = 1'b0;
      reg_write = 1'b1;
      write_back_source = 2'b11;
      branch = 1'b0;
      jump = 1'b0;
      itype_src2_rs1 = 1'b1; // We need this for u-type as well
      case(op[0])
        1'b1: second_add_source = 2'b01; // lui
        1'b0: second_add_source = 2'b00; // auipc
      endcase
    end
    //EVERYTHING ELSE
    default: begin
        reg_write = 1'b0;
        imm_source = 3'b000;
        mem_write = 1'b0;
        alu_op = 2'b00;
        write_back_source = 2'b00;
        branch = 1'b0;
        jump = 1'b0;
        itype_src2_rs1 = 1'b0;
        second_add_source = 2'b00;
      end
    endcase
  end

  // ADDED TO DEAL WITH CHANGING DESTINATION TO R1 FOR BRANCH INSTRUCTIONS
assign branch_inst = branch;

/**
* ALU DECODER
*/

always_comb begin
    case (alu_op)
        // LW, SW
        2'b00: alu_control = 4'h0;
        // R-Types
        2'b10: begin
          //if anyone looks at this that isn't the original author
          //just know that this is inherited from a RISC-V CPU and I just liked to keep it like this
          //for the sake of labeling and keeping track.
          //Probably can just put everything below as alu_control = func4;
          case (func4)
            // ADD (SUB will NOT utilize F8, and for now there is no F8)
            4'h0: alu_control = 4'h0;
            // AND
            4'h1: alu_control = 4'h1;
            // OR
            4'h2: alu_control = 4'h2;
            // SUB
            4'h3: alu_control = 4'h3;
            //SLT (and SLTI)
            4'h4: alu_control = 4'h4;
            //SLTIU
            4'h5: alu_control = 4'h5;
            // XOR
            4'h6: alu_control = 4'h6;
            // SLL
            4'h7: alu_control = 4'h7;
            // SRL
            4'h8: alu_control = 4'h8;
            // SRA
            4'h9: alu_control = 4'h9;
            // NE
            4'hA: alu_control = 4'hA;
            // SGT (Set Greater Than)
            4'hB: alu_control = 4'hB;
            // SGTU (Set Greater Than unsigned)
            4'hC: alu_control = 4'hC;
            // ALL THE OTHERS
            default: alu_control = 4'hF;
          endcase
        end
        2'b01: begin
          case (func4)
            // BEQ
            4'h3: alu_control = 4'h3;
            // BLT
            4'h4: alu_control = 4'h4;
            // BLTU
            4'h5: alu_control = 4'h5;
            // BNE
            4'hA: alu_control = 4'hA;
            // BGT
            4'hB: alu_control = 4'hB;
            // BGTU
            4'hC: alu_control = 4'hC;
            default: alu_control = 4'h0;
          endcase
        end
        // EVERYTHING ELSE
        2'b11: alu_control = 4'hF;
       // default: alu_control = 4'b1111;
    endcase
end

logic assert_branch;

//Jumpscared into requesting func4? Nope! I'll just use the opcode!
always_comb begin: branch_logic_decode
  case (op)
    //BEQ
    16'hD003: assert_branch = alu_zero & branch;
    //BLT, BLTU, BNE, BGT
    16'hD004, 16'hD005, 16'hD00A, 16'hD00B, 16'hD00C: assert_branch = alu_last_bit & branch;
    default : assert_branch = 1'b0;
  endcase
end

/*
* pc_source
*/
assign pc_source = assert_branch | jump;

endmodule
