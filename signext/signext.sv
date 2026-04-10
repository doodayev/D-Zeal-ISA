//signext.sv

/* I was tempted to change raw_src to [39:0] but that may cause problems
with ease of emulation since C compilers can't handle 40-bits directly (probably have to use a 64-bit integer)
and also because it would be the only thing in the entire design that isn't an 8, 16, 32, or
64-bit number. As you can see those are all "standard" widths.

There may also be problems with programmers wishing they could do 40-bit jumps with branches.
They'd ask "why can I do a 40-bit unconditional but not a 40-bit branch?"
The target of my ISA is a beginner and beginners ask these type of questions.

But more importantly it affects THE REST of the design. cpu.sv and alu.sv would have to be aware
of this as well. People may want to load 40-bit immediates somehow to do a jump and they'd waste
two instructions to do that (an upper 8-bit load immediate and a lower 32-bit load immediate). */

module signext (
    //IN
    input logic [31:0] raw_src,
    input logic [2:0] imm_source,
    //OUT (immediate)
    output logic [63:0] immediate
    );

   // logic [31:0] gathered_imm;

    always_comb begin
        case(imm_source)
            // For I-Types
            3'b000: immediate = {{32{raw_src[31]}}, raw_src};
            // For S-types
            3'b001: immediate = {{32{raw_src[31]}}, raw_src};
            // For B-types
            3'b010: immediate = {{32{raw_src[31]}}, raw_src};
            // For J-types (Yeah guess what? Same thing again haha!)
            3'b011: immediate = {{32{raw_src[31]}}, raw_src};
            // U-types are actually different for once
            3'b100: immediate = {raw_src, 32'h00000000};
            default: immediate = 64'b0;
        endcase
    end

    // assign immediate = {{32{raw_src[31]}}, raw_src};

endmodule
