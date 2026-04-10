import cocotb
from cocotb.triggers import Timer
import random

from cocotb.types import Logic
from cocotb.types import LogicArray

#@cocotb.coroutine
#https://docs.cocotb.org/en/stable/coroutines.html coroutines are no longer needed?
#Changed in version 1.4: The cocotb.coroutine decorator is no longer necessary for async def
#coroutines. async def coroutines can be used, without the @cocotb.coroutine decorator, wherever
#decorated coroutines are accepted, including yield statements and cocotb.fork (since replaced with
#start_soon()).

#Oh ok this guy already put the async def but for some reason also had put the
#cocotb.coroutine decorator

async def set_unknown(dut):
    #Set all input to unknown before each test
    await Timer(1, unit="ns")
    dut.op.value = LogicArray("XXXXXXXXXXXXXXXX")
    #
    #Uncomment the follwoing throughout the course when needed
    #
    #dut.func3.value = Logic("XXX")
    #dut.func7.value = Logic("XXXXXXXX")
    #dut.alu_zero.value = Logic("X")
    #dut.alu_last_bit.value = Logic("X")
    await Timer(1, unit="ns")

@cocotb.test()
async def lw_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR LW
    await Timer(1, unit="ns")
    dut.op.value = 0xB010 #lw
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0000"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.pc_source.value == "0"
    await Timer(10, unit="ns")

@cocotb.test()
async def sw_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SW
    await Timer(10, unit="ns")
    dut.op.value = 0xC010 #SW
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0000"
    assert dut.imm_source.value == "001"
    assert dut.mem_write.value == "1"
    assert dut.reg_write.value == "0"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def add_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR ADD
    await Timer(10, unit="ns")
    dut.op.value = 0xA000 # R-TYPE
    # Watch out! F4 is important here and now!
    dut.func4.value = 0x0
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def and_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR ADD
    await Timer(10, unit="ns")
    dut.op.value = 0xA001 # R-TYPE
    # Watch out! F4 is important here and now!
    dut.func4.value = 0x1
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0001"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def or_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR OR
    await Timer(10, unit="ns")
    dut.op.value = 0xA002 # R-TYPE
    dut.func4.value = 0x2
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0010"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def beq_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BEQ
    await Timer(10, unit="ns")
    dut.op.value = 0xD003 # B-TYPE (beq), 0xC003 since that's corresponding with func4 and alu control
    dut.func4.value = 0x3
    dut.alu_zero.value = 0b0 #french dude added the alu_zero requirement for some reason
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == "0011"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_zero.value = 0b1 #investigate alu_zero
    await Timer(1, unit="ns")
    assert dut.pc_source.value == "1"

@cocotb.test()
async def jal_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR JAL
    await Timer(10, unit="ns")
    dut.op.value = 0xE010 #J-TYPE
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "011"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.branch.value == "0"
    assert dut.jump.value == "1"
    assert dut.pc_source.value == "1"
    assert dut.write_back_source.value == "10"

@cocotb.test()
async def addi_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR ADDI
    await Timer(10, unit="ns")
    dut.op.value = 0xB000 #I-TYPE ADDI
    dut.func4.value = 0x0 #ADDI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0000" #we seek to perform addition
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def auipc_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR AUIPC
    await Timer(10, unit="ns")
    dut.op.value = 0xF010 # U-TYPE (auipc)
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.imm_source.value == "100"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.write_back_source.value == "11"
    assert dut.branch.value == "0"
    assert dut.jump.value == "0"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def slti_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SLTI
    await Timer(10, unit="ns")
    dut.op.value = 0xB004 #I-TYPE (alu)
    dut.func4.value = 0x4 #SLTI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0100"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sltiu_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SLIT
    await Timer(10, unit="ns")
    dut.op.value = 0xB005 #I-TYPE (alu)
    dut.func4.value = 0x5
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0101"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def xori_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR XORI
    await Timer(10, unit="ns")
    dut.op.value = 0xB006 # I-TYPE (alu)
    dut.func4.value = 0x6 #xori
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0110"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def ori_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR ORI
    await Timer(10, unit="ns")
    dut.op.value = 0xB002 #I-TYPE ORI
    dut.func4.value = 0x2 #ORI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0010" #we seek to perform OR
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def andi_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR ANDI
    await Timer(10, unit="ns")
    dut.op.value = 0xB001 #I-TYPE ANDI
    dut.func4.value = 0x1 #ANDI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0001" #we seek to perform AND
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def slli_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SLLI
    await Timer(10, unit="ns")
    dut.op.value = 0xB007 #I-TYPE SLLI
    dut.func4.value = 0x7 #SLLI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "0111" #we seek to perform SHIFT LEFT
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def srli_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SRLI
    await Timer(10, unit="ns")
    dut.op.value = 0xB008 #I-TYPE SRLI
    dut.func4.value = 0x8 #SRLI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "1000" #we seek to perform SRLI
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def srai_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR SRAI
    await Timer(10, unit="ns")
    dut.op.value = 0xB009 #I-TYPE SRAI
    dut.func4.value = 0x9 #SRAI
    await Timer(1, unit="ns")

    #Logic block controls
    assert dut.alu_control.value == "1001" #we seek to perform SRAI
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sub_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SUB
    await Timer(10, unit="ns")
    dut.op.value = 0xA003 # R-TYPE
    dut.func4.value = 0x3
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0011"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def slt_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SLT
    await Timer(10, unit="ns")
    dut.op.value = 0xA004 # R-TYPE
    dut.func4.value = 0x4
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0100"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sltu_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SLTU
    await Timer(10, unit="ns")
    dut.op.value = 0xA005 # R-TYPE
    dut.func4.value = 0x5
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0101"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def xor_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR XOR
    await Timer(10, unit="ns")
    dut.op.value = 0xA006 # R-TYPE
    dut.func4.value = 0x6
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0110"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sll_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SLL
    await Timer(10, unit="ns")
    dut.op.value = 0xA007 # R-TYPE
    dut.func4.value = 0x7
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0111"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def srl_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SRL
    await Timer(10, unit="ns")
    dut.op.value = 0xA008 # R-TYPE
    dut.func4.value = 0x8
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "1000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sra_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR SRA
    await Timer(10, unit="ns")
    dut.op.value = 0xA009 # R-TYPE
    dut.func4.value = 0x9
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "1001"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    #Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def blt_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BLT
    await Timer(10, unit="ns")
    dut.op.value = 0xD004
    dut.func4.value = 0x4
    dut.alu_last_bit.value = 0x0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == 0x4
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"
    assert dut.second_add_source.value == "00"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_last_bit.value = 0x1
    await Timer(1,unit="ns")
    assert dut.pc_source.value == "1"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def bne_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BNE
    await Timer(10, unit="ns")
    dut.op.value = 0xD00A
    dut.func4.value = 0xA
    dut.alu_last_bit.value = 0x0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == 0xA
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"
    assert dut.second_add_source.value == "00"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_last_bit.value = 0x1
    await Timer(1,unit="ns")
    assert dut.pc_source.value == "1"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def bgt_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BLT
    await Timer(10, unit="ns")
    dut.op.value = 0xD00B
    dut.func4.value = 0xB
    dut.alu_last_bit.value = 0x0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == 0xB
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"
    assert dut.second_add_source.value == "00"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_last_bit.value = 0x1
    await Timer(1,unit="ns")
    assert dut.pc_source.value == "1"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def bltu_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BLTU
    await Timer(10, unit="ns")
    dut.op.value = 0xD00B
    dut.func4.value = 0xB
    dut.alu_last_bit.value = 0x0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == 0xB
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"
    assert dut.second_add_source.value == "00"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_last_bit.value = 0x1
    await Timer(1,unit="ns")
    assert dut.pc_source.value == "1"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def bgtu_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR BGT
    await Timer(10, unit="ns")
    dut.op.value = 0xD00C
    dut.func4.value = 0xC
    dut.alu_last_bit.value = 0x0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == 0xC
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"
    assert dut.second_add_source.value == "00"

    #Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_last_bit.value = 0x1
    await Timer(1,unit="ns")
    assert dut.pc_source.value == "1"
    assert dut.second_add_source.value == "00"

@cocotb.test()
async def jalr_control_test(dut):
    await set_unknown(dut)
    #TEST CONTROL SIGNALS FOR JALR
    await Timer(10, unit="ns")
    dut.op.value = 0xBE00
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.branch.value == "0"
    assert dut.jump.value == "1"
    assert dut.pc_source.value == "1"
    assert dut.write_back_source.value == "10"
    assert dut.second_add_source.value == "10"

