#test_cpu.py

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

def binary_to_hex(bin_str):
    #Convert binary string to hexadecimal
    hex_str = hex(int(str(bin_str), 2))[2:]
    hex_str = hex_str.zfill(8)
    return hex_str.upper()

def hex_to_bin(hex_str):
    #Convert hex str to bin
    bin_str = bin(int(str(hex_str), 16))[2:]
    hex_str = hex_str.zfill(8)
    return hex_str.upper()

async def cpu_reset(dut):
    #Init and reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)   #Wait for a clock edge after reset
    dut.rst_n.value = 1         #De-assert reset
    await RisingEdge(dut.clk)   #Wait for a clock edge after reset

#@cocotb.test()
#async def cpu_init_test(dut):
#    """Reset the cpu and check for a good imem read"""
#    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
#    await RisingEdge(dut.clk)

#    await cpu_reset(dut)
#    assert binary_to_hex(dut.pc.value) == "00000000"

    #Load the expected instruction memory as binary
    #Note that this is loaded in sim directly via the verilog code
    #This load is only for expected
#    imem = []
#    with open("test_imemory.hex", "r") as file:
#        for line in file:
            #Ignore comments
#            line_content = line.split("//")[0].strip()
#            if line_content:
#                imem.append(hex_to_bin(line_content))

    #We limit this initial test to the first couple of instructions
    #as we'll later implement branches
#    for counter in range(5):
#        expected_instruction = imem[counter]
#        assert dut.instruction.value == expected_instruction
#        await RisingEdge(dut.clk)

@cocotb.test()
async def cpu_insrt_test(dut):
    """Runs a lw datapath test"""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    await RisingEdge(dut.clk)
    await cpu_reset(dut)

    ##################
    # LOAD WORD TEST
    #lw x18 0x8(x0)
    ##################
    print("\n\nTESTING LoadWorld\n\n")

    #The first instruction for the test in imem.hex load the data from
    #dmem @ address 0x00000008 that happens to be 0xDEADBEEF into register x18

    #Wait a clock cycle for the instruction to execute
    await RisingEdge(dut.clk)

    print(binary_to_hex(dut.regfile.registers[18].value))

    #Check the value of reg x18
    assert binary_to_hex(dut.regfile.registers[18].value) == "CAFEBABEDEADBEEF"

    ##################
    # STORE WORLD TEST (yes, THE WORLD)
    # sw x18 0x18(x0)
    ##################
    print("\n\nTESTING Store WORLD\n\n")
    test_address = int(0x18 / 8) #mem is byte addressed but is made out of words in the eyes of the software

    #The second instruction for the test in imem.hex stores the data from
    # x18 (that happens to be 0xDEADBEEF from the previous LW test) @ address 0x0000000C

    #First, let's check the initial value
    assert binary_to_hex(dut.data_memory.mem[test_address].value) == "F2F2F2F2F2F2F2F2"

    #Wait a clock cycle for the instruction to execute
    await RisingEdge(dut.clk)
    #Check the value of mem[0xC]
    assert binary_to_hex(dut.data_memory.mem[test_address].value) == "CAFEBABEDEADBEEF"

    ##################
    # ADD TEST
    # lw R19 0x20(R0)
    # add R20 R18 R19
    ##################

    #Expected result of R18 + R19
    expected_result = (0xCAFEBABEDEADBEEF + 0x0000000000080486) & 0xFFFFFFFFFFFFFFFF
    await RisingEdge(dut.clk) #lw R19 0x20(R0)
    assert binary_to_hex(dut.regfile.registers[19].value) == "00080486"
    await RisingEdge(dut.clk) #add R20 R18 R19
    assert binary_to_hex(dut.regfile.registers[20].value) == hex(expected_result)[2:].upper()
    print(hex(expected_result)[2:].upper())

    ##################
    # AND TEST
    # and R21 R18 R20
    ##################

    #Use last expected result, as this instruction uses last op result register
    expected_result = expected_result & 0xCAFEBABEDEADBEEF
    await RisingEdge(dut.clk) # and R21, R18 R20
    assert binary_to_hex(dut.regfile.registers[21].value) == hex(expected_result)[2:].upper()
    print(hex(expected_result)[2:].upper())

    ##################
    # OR TEST
    # Changing up the values a bit
    # lw R5 0x30(R0)
    # lw R6 0x38(R0)
    # or R7, R5 R6 <- should result in 0x8800000022426D86
    ##################
    print("\n\nTESTING OR\n\n")

    await RisingEdge(dut.clk) #lw R5 0x30(x0) | R5 <= 0x6502
    assert binary_to_hex(dut.regfile.registers[5].value) == "8800000000006502"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[6].value) == "23000022426886"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[7].value) == "8823000022426D86"

    ##################
    # BEQ TEST
    # beq R6, R7, 0xC (shouldn't branch)
    # lw R22 0x8(R0)
    # beq R18 R22 0x20
    # nop
    # nop
    # beq R0 R0 0x18
    # lw R22 R0 0x0
    # beq R22 R22 -0x8
    ##################
    print("\n\nTESTING BEQ\n\n")

    #assert binary_to_hex(dut.instruction.value) == "D003060700000018" D003000000000018
    assert binary_to_hex(dut.instruction.value) == "D003150700000018"
    await RisingEdge(dut.clk) #beq R6, R7, 0x18 (shouldn't branch)
    #Check if the current instruciton is the one we expected
    assert binary_to_hex(dut.instruction.value) == "B014160000000010"

    await RisingEdge(dut.clk) #lw R22 0x10(R0)
    assert binary_to_hex(dut.regfile.registers[22].value) == "CAFEBABEDEADBEEF"

    await RisingEdge(dut.clk) #beq R18 R22 0x20
    #Check if the current instruction is the one we expected
    print(binary_to_hex(dut.regfile.registers[22].value))
    print(binary_to_hex(dut.regfile.registers[18].value))
    assert binary_to_hex(dut.instruction.value) == "B014160000000000"

    await RisingEdge(dut.clk) #lw R22 R0(x0)
    assert binary_to_hex(dut.regfile.registers[22].value) == "AEAEAEAEAEAEAEAE"

    await RisingEdge(dut.clk) #beq R22 R22 -0x10 TAKEN
    #Check instruction
    assert binary_to_hex(dut.instruction.value) == "D003000000000018"

    await RisingEdge(dut.clk) #beq R0 R0 0x18 TAKEN
    #Check if the current instruction is the one we expected
    assert binary_to_hex(dut.instruction.value) == "00000000"

    ##################
    # E010010000000018 // JAL TEST START       : jal R1 0x18
    # 0000000000000000 // NOP                  : nop
    # E010010000000018 //                      : jal R1 0x18
    # E0100100FFFFFFF8 //                      : jal R1 -0x08
    # 0000000000000000 // NOP                  : nop
    # B014070000000018 //                      : lw R7 0x18
    ##################
    print("\n\nTESTING JAL\n\n")

    #Check the test's init state
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "E010010000000018"
    assert binary_to_hex(dut.pc.value) == "00000088"

    await RisingEdge(dut.clk) #jal R1 0x18
    #Check new state and return address (R1) register value
    assert binary_to_hex(dut.instruction.value) == "E0100100FFFFFFF8"
    assert binary_to_hex(dut.pc.value) == "000000A0"
    assert binary_to_hex(dut.regfile.registers[1].value) == "00000090" #stored old pc + 8

    await RisingEdge(dut.clk) #jal R1 -0x8
    #Check new state and return address (R1) register value
    assert binary_to_hex(dut.instruction.value) == "E010010000000018"
    assert binary_to_hex(dut.pc.value) == "00000098"
    assert binary_to_hex(dut.regfile.registers[1].value) == "000000A8" #stored old pc + 8

    await RisingEdge(dut.clk) #jal R1 0xC
    #Check new state and return address (R1) register value
    assert binary_to_hex(dut.instruction.value) == "B014070000000018"
    assert binary_to_hex(dut.pc.value) == "000000B0"
    assert binary_to_hex(dut.regfile.registers[1].value) == "000000A0" #stored old pc + 8

    await RisingEdge(dut.clk) #lw R7 0xC(R0)
    assert binary_to_hex(dut.regfile.registers[7].value) == "CAFEBABEDEADBEEF"

    ##################
    # ADDI TEST
    # B00019070000007F // ADDI TEST START      :B8 addi R26, R7 0x7F
    # B0001806FFFF9AFE //                      :C0 addi R25, R6 -0x6502
    ##################
    print("\n\nTESTING ADDI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B0001A070000007F"
    assert not binary_to_hex(dut.regfile.registers[26].value) == "CAFEBABEDEADBF6E"

    await RisingEdge(dut.clk) #addi R26 R7 0x7F
    assert binary_to_hex(dut.instruction.value) == "B0001906FFFF9AFE"
    assert binary_to_hex(dut.regfile.registers[26].value) == "CAFEBABEDEADBF6E"

    await RisingEdge(dut.clk) #addi R25 R6 0x9AFE
    assert binary_to_hex(dut.regfile.registers[25].value) == "23000022420384"

    ##################
    # AUIPC TEST (PC before is 0xC8 (or maybe C0))
    # F010050068696768 // AUIPC TEST START     :C8 auipc R5 0x68696768
    ##################
    print("\n\nTESTING AUIPC\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "F010050068696768"

    await RisingEdge(dut.clk) #auipc R5 0x68696768
    assert binary_to_hex(dut.regfile.registers[5].value) == "68696768000000C8"

    ##################
    # LUI TEST
    # F011050062796521 // LUI                  :D0 lui R5 0x62796521
    ##################
    print("\n\nTESTING LUI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "F011050062796521"

    await RisingEdge(dut.clk) #lui R5 0x62796521
    assert binary_to_hex(dut.regfile.registers[5].value) == "6279652100000000"

    ##################
    # B0041713FFFFFFFF // SLTI TEST START      :D8 slti R23 R19 0xFFFFFFFF
    # B004171700000001 //                      :E0 slti R23 R23 0x1
    ##################
    print("\n\nTESTING SLTI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.regfile.registers[19].value) == "00080486"
    assert binary_to_hex(dut.instruction.value) == "B0041713FFFFFFFF"

    await RisingEdge(dut.clk) #slti R23 R19 0xFFFFFFFF
    assert binary_to_hex(dut.regfile.registers[23].value) == "00000000"

    await RisingEdge(dut.clk) #slti R23 R23 0x00000001
    assert binary_to_hex(dut.regfile.registers[23].value) == "00000001"

    ##################
    # B0051613FFFFFFFF // SLTIU TEST START     :E8 sltiu R22 R19 0xFFFFFFFF
    # B005161300000001 //                      :F0 sltiu R22 R19 0x1
    ##################
    print("\n\nTESTING SLTIU\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B0051613FFFFFFFF"

    await RisingEdge(dut.clk) #sltiu R22 R19 0xFFFFFFFF
    assert binary_to_hex(dut.regfile.registers[22].value) == "00000001"

    await RisingEdge(dut.clk) #sltiu R22 R19 0x00000001
    assert binary_to_hex(dut.regfile.registers[22].value) == "00000000"

    ##################
    # B006151600068000 // XORI TEST START      :F8 xori R18 R19 0x68000
    # B006161500000000 //                      :100 xori R19 R18 0x0000
    ##################
    print("\n\nTESTING XORI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B006121300068000"  #E8486

    await RisingEdge(dut.clk) #xori R18 R19 0x68000
    assert binary_to_hex(dut.regfile.registers[18].value) == "000E8486"

    await RisingEdge(dut.clk) #xori R19 R18 0x0000
    assert(dut.regfile.registers[18].value == dut.regfile.registers[19].value)

    ##################
    #B000A0000000F00F //                      :108 lw R161 R0 0xF00F
    #B001A0A0F33D533D // ANDI TEST            :110 andi R161 R0 0xF33D533D
    ##################
    print("\n\nTESTING ANDI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A0000000F00F"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[160].value) == "0000F00F" #Did it load right?

    assert binary_to_hex(dut.instruction.value) == "B001A0A0F33D533D"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[160].value) == "0000500D"

    ##################
    #B000A10000000235 //                      :118 addi R161 R0 0x235
    #B002A1A100002500 // ORI TEST             :120 ori R161 R161 0x2500
    ##################
    print("\n\nTESTING ORI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A10000000235"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[161].value) == "00000235"

    assert binary_to_hex(dut.instruction.value) == "B002A1A100002500"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[161].value) == "00002735"

    ##################
    #B000A2000C000000 // SLLI TEST            :128 addi R162 R0 0xCC000000
    #B007A20000000008 //                      :130 slli R162 R0 0x8
    ##################
    print("\n\nTESTING SLLI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A2000C000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[162].value) == "0C000000"

    assert binary_to_hex(dut.instruction.value) == "B007A2A200000008"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[162].value) == "C00000000"

    ##################
    #B000A30000515000 // SRLI TEST            :138 addi R163 R0 0x515000
    #B008A3A30000000C //                      :140 srli R163 R163 0xC
    ##################
    print("\n\nTESTING SRLI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A30000515000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[163].value) == "00515000"

    assert binary_to_hex(dut.instruction.value) == "B008A3A30000000C"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[163].value) == "00000515"

    ##################
    #B000A400FF789777 // SRAI TEST            :148 addi R164 R0 0xFF789777
    #B009A4A400000010 //                      :150 srai R164 R164 0x10
    ##################
    print("\n\nTESTING SRAI\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A400FF789777"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[164].value) == "FFFFFFFFFF789777"

    assert binary_to_hex(dut.instruction.value) == "B009A4A400000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[164].value) == "FFFFFFFFFFFFFF78"

    ##################
    #B000A60000001991 // SUB TEST             :158 addi R165 R0 0x1991
    #B000A50000001453 //                      :160 addi R166 R0 0x1453
    #A003A7A5A6000000 //                      :168 sub R178, R165 R166
    ##################
    print("\n\nTESTING SUB\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "B000A60000001991"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[166].value) == "00001991"

    assert binary_to_hex(dut.instruction.value) == "B000A50000001453"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[165].value) == "00001453"

    assert binary_to_hex(dut.instruction.value) == "A003A7A5A6000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[167].value) ==  "0000053E"

    ##################
    #A004A819A5000000 // SLT TEST      :170 slt R168, R25 R165    (R168 = 1, because 0x1453 > -0x6502)
    ##################
    print("\n\nTESTING SLT\n\n")

    assert binary_to_hex(dut.instruction.value) == "A004A819A5000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[168].value) == "00000001"

    ##################
    #A007A9A8A7000000 // SLL TEST             :178 sll R169, R165 R168 (R169 = 53E << 1 = A7C)
    ##################
    print("\n\nTESTING SLL\n\n")

    assert binary_to_hex(dut.regfile.registers[167].value) == "0000053E"
    assert binary_to_hex(dut.instruction.value) == "A007A9A8A7000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[169].value) == "00000A7C"

    ##################
    #A005AAA6A5000000 // SLTU TEST            :180 sltu R170, R166 R165 (R170 = 1, because 0x1991 > 0x1453)
    ##################
    print("\n\nTESTING SLTU\n\n")

    assert binary_to_hex(dut.instruction.value) == "A005AAA6A5000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[170].value) == "00000001"

    ##################
    #A008A9AAA9000000 // SRL TEST             :188 srl R169, 169 170 (R168 = A7C >> 1 = 53E)
    ##################
    print("\n\nTESTING SRL\n\n")

    assert binary_to_hex(dut.instruction.value) == "A008A9AAA9000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[169].value) == "0000053E"

    ##################
    #B000AAAAD00DFEED // SRA TEST           :190 addi R170, R170 0xD00DFEEE
    #B000ABAB00000011 //                    :198 addi R171, R171 0x11
    #A009ACABAA000000 //                    :1A0 sra  R172, R171 R170 (R172 = 0xD00DFEEE >> 0x11 = 0x6806)
    ##################
    print("\n\nTESTING SRA\n\n")

    assert binary_to_hex(dut.instruction.value) == "B000AAAAD00DFEED"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[170].value) == "FFFFFFFFD00DFEEE"

    assert binary_to_hex(dut.instruction.value) == "B000ABAB00000011"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[171].value) == "00000011"

    assert binary_to_hex(dut.instruction.value) == "A009ACABAA000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[172].value) == "FFFFFFFFFFFFE806"

    ##################
    #A006ADAAAA000000 // XOR TEST             :1A8 xor R173, R170 R170 (R173 = 0)
    #################
    print("\n\nTESTING XOR\n\n")

    assert binary_to_hex(dut.instruction.value) == "A006ADAAAA000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[173].value) == "00000000"

    ##################
    #D004A6A500000010 // BLT TEST             :1B0 blt R166 R165 0x10
    #D004A5A600000010 //                      :1B8 blt R165 R166, 0x10 (taken, R166 < R165)
    #A00019A113000000 //                      :1C0 add R25, R161 R22 (this shouldn't even be taken)
    #B000770000000077 //                      :1C8 add R119, R0 0x77 (haha. This happens though)
    ##################
    print("\n\nTESTING BLT\n\n")

    assert binary_to_hex(dut.instruction.value) == "D004A6A500000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D004A5A600000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "B000770000000077"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[119].value) == "00000077"

    ##################
    #A000787700000000 // BNE TEST             :1D0 add R120, R119, R0
    #D00A777800000010 //                      :1D8 bne R119 R120, 0x10
    #D00A77A600000018 //                      :1E0 bne R119 R166, 0x18
    #A000121212000000 //                      :1E8 add R18, R18 R18
    #A000121212000000 //                      :1F0 add R18, R18 R18
    #A000131206000000 //                      :1F8 add R19, R18 R6
    #B000777700000001 //                      :200 addi R119, R119 0x2
    ##################
    print("\n\nTESTING BNE\n\n")

    assert binary_to_hex(dut.instruction.value) == "A000787700000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D00A777800000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D00A77A600000020"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "B000777700000001"
    await RisingEdge(dut.clk)

    ##################
    #D00BA6A500000018 // BGT TEEST            :208 bgt R165 R166 0x18
    #A003121212000000 //                      :210 sub R18, R18 R18
    #A003121212000000 //                      :218 sub R18, R18 R18
    #D00BA5A600000010 //                      :220 bgt R166 R165 0x10
    #A000050000000000 //                      :228 add R5, R0 R0
    #B000050500000005 //                      :230 addi R5, R5 0x5
    ##################
    print("\n\nTESTING BGT\n\n")

    assert binary_to_hex(dut.instruction.value) == "D00BA6A500000018"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D00BA5A600000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "A000050000000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[5].value) == "00000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[5].value) == "00000005"

    ##################
    #A000070500000000 // BGTU  TEST           :238 add R7, R5 R0
    #B000070700000002 //                      :240 addi R7, R7 0x2
    #D00C070500000018 //                      :248 bgtu R7 R5, 0x10
    #A003070705000000 //                      :250 sub R7, R5 R7
    #A003AC07AA000000 //                      :258 sub R172, R7 R170
    #A000080705000000 //                      :260 add R8, R5 R7
    ##################
    print("\n\nTESTING BGTU\n\n")

    assert binary_to_hex(dut.instruction.value) == "A000070500000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "B000070700000002"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D00C070500000018"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "A000080705000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[5].value) == "00000005"
    assert binary_to_hex(dut.regfile.registers[7].value) == "00000007"

    ##################
    #D00C000500000010 //                      :268 bgtu R0 R5, 0x10
    #D005000500000010 // BLTU TEST            :270 bltu R0 R5, 0x10
    #A000090805000000 //                      :278 add R8, R8 R5
    #A000090807000000 //                      :280 add R9, R8 R7
    #D0050500FFFFFFF8 //                      :288 bltu R05 R0, -0x8
    #B0000C0000000002 //                      :290 addi R0 0x2, R12
    #A0000D0000000000 //                      :298 add R13, R0 R0
    ###################
    print("\n\nTESTING BLTU\n\n")

    assert binary_to_hex(dut.instruction.value) == "D00C000500000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D005000500000010"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "A000090807000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "D0050500FFFFFFF8"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "B0000C0000000002"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "A0000D0000000000"
    assert binary_to_hex(dut.regfile.registers[12].value) == "00000002"
    await RisingEdge(dut.clk)

    ##################
    #B0000D0D000002B8 // JALR TEST            :300 addi R13, R13 0x2B8
    #BE000E0D00000000 //                      :308 jalr R14, R13, 0x0
    #B0000C0C00000005 //                      :310 addi R12, R12 0x5
    #B0000C0C00000007 //                      :318 addi R12, R12 0x7
    ##################
    print("\n\nTESTING JALR\n\n")

    assert binary_to_hex(dut.instruction.value) == "B0000D0D000002B8"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "BE000E0D00000000"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[14].value) == "000002B0"
    assert binary_to_hex(dut.instruction.value) == "B0000C0C00000007"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[12].value) == "00000009"
    await RisingEdge(dut.clk)

    ##################
    #C014AA0000000045 //                      :2C8 StoreWorld R170, R0 0x45 (NOT taken, misaligned)
    #C010AA000000000B //                      :2D0 Steigth R170, R0 0xB
    ##################
    print("\n\nTESTING Steigth\n\n")

    #Check test's init state
    assert binary_to_hex(dut.instruction.value) == "C01401AA00000045"

    await RisingEdge(dut.clk) #sword R170, R0 0x45
    assert binary_to_hex(dut.data_memory.mem[8].value) == "5567623006457022" #maintains previous value

    await RisingEdge(dut.clk) #sbyte R170, R0 0xA
    print("R170 =", hex(dut.regfile.registers[170].value.to_unsigned()))
    assert binary_to_hex(dut.regfile.registers[170].value) == "FFFFFFFFD00DFEEE"
    print(binary_to_hex(dut.data_memory.mem[1].value))
    assert binary_to_hex(dut.data_memory.mem[1].value) == "123456789EECDEF"


    ##################
    #B000A000033D533D //                      :2D8 addi R160, AA 0x033D533D
    #C01103A000000058 // s2pac/s2byte/s2quart :2D8 s2pac R3, R160 0x58
    #C01104A000000066 //                      :2E8 s2pac R4, R160 0x65
    #C01105A000000063 //                      :2F0 s2pac R5, R160 0x63 (NOT taken, misaligned)
    ##################
    print("\n\nTESTING Store2pac\n\n")

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "C01103A000000058"
    print("R170 =", hex(dut.regfile.registers[170].value.to_unsigned()))
    await RisingEdge(dut.clk)
    print ("Memory Address 11 = ", hex(dut.data_memory.mem[11].value))
    assert binary_to_hex(dut.data_memory.mem[11].value) == "5A656D6C7961533D"

    await RisingEdge(dut.clk)
    print ("Memory Address 12 = ", hex(dut.data_memory.mem[12].value))
    assert binary_to_hex(dut.data_memory.mem[12].value) == "533D004768616472"
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.data_memory.mem[12].value) == "533D004768616472"

    ##################
    #B000C1C147616E67 //                      :2F8 addi R193, R193 0x47616E67
    #C01206C10000006C //                      :300 StoreChud R6, R193 0x6C
    ##################
    print("\n\n TESTING StoreChud\n\n")
    assert binary_to_hex(dut.instruction.value) == "B000C1C147616E67"
    await RisingEdge(dut.clk)
    print("R193 =", hex(dut.regfile.registers[193].value.to_unsigned()))
    assert binary_to_hex(dut.instruction.value) == "C01206C10000006C"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.data_memory.mem[13].value) == "47616E675075636B"
    print ("Memory Address 13 = ", hex(dut.data_memory.mem[13].value))

    ##################
    #B010C2000000002A //                      :308 LoadSquad R194, R0 0x2A
    #B019C20000000028 //                      :308 Load2pacU R194, R0 0x28
    #B011C30000000028 //                      :310 Load2pac R195, R0 0x28
    #B012C40000000044 //                      :318 LoadChud R196, R0 0x44
    ###################
    print("\n\n TESTING LoadSquad\n\n")
    assert binary_to_hex(dut.instruction.value) == "B010C2000000002A"
    await RisingEdge(dut.clk)
    print("R194 =", hex(dut.regfile.registers[194].value.to_unsigned()))
    assert binary_to_hex(dut.regfile.registers[194].value) == "00000077"

    print("\n\n TESTING 2pacU\n\n")
    assert binary_to_hex(dut.instruction.value) == "B019C20000000028"
    await RisingEdge(dut.clk)
    print("R194 =", hex(dut.regfile.registers[194].value.to_unsigned()))
    assert binary_to_hex(dut.regfile.registers[194].value) == "00008888"

    print("\n\n TESTING 2pac\n\n")
    assert binary_to_hex(dut.instruction.value) == "B011C30000000028"
    await RisingEdge(dut.clk)
    print("R195 =", hex(dut.regfile.registers[195].value.to_unsigned()))
    assert binary_to_hex(dut.regfile.registers[195].value) == "FFFFFFFFFFFF8888"

    print("\n\n TESTING Chud \n\n")
    assert binary_to_hex(dut.instruction.value) == "B012C40000000044"
    await RisingEdge(dut.clk)
    print("R196 =", hex(dut.regfile.registers[196].value.to_unsigned()))
    assert binary_to_hex(dut.regfile.registers[196].value) == "55676230"

    print("\n ENOUGH!!!!! THAT'S ENOUGH TESTING FOR THE SIMULATED SINGLE CYCLE ZEAL CPU! \n")
