import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random
import numpy as np

@cocotb.test()
async def random_write_read_test(dut):
    """Test positive immediate = 224257427 with source = 0"""
    await Timer(1, unit="ns")

    # 32-bit positive number
    raw_val = 224257427
    dut.raw_src.value = raw_val
    dut.imm_source.value = 0          # 3-bit 0

    await Timer(1, unit="ns")          # allow propagation

    # Expected 64-bit sign-extended value
    # high 32 bits = 0, low 32 bits = 224257427 (0xD5DE593)
    expected_bin = "00000000000000000000000000000000" + \
                   "00001101010111011110010110010011"   # 64 bits total
    expected_int = raw_val               # positive, same integer value

    actual_int = int(dut.immediate.value)
    assert actual_int == expected_int, f"Integer mismatch: expected {expected_int}, got {actual_int}"
    assert dut.immediate.value.binstr == expected_bin, \
           f"Binary mismatch:\n expected {expected_bin}\n got      {dut.immediate.value.binstr}"

@cocotb.test()
async def random_negative_write_read_test(dut):
    """Test negative immediate = -42 with source = 0"""
    await Timer(1, unit="ns")

    # 32-bit two's complement representation of -42
    raw_val = (1 << 32) - 42            # 0xFFFFFFD6
    dut.raw_src.value = raw_val
    dut.imm_source.value = 0

    await Timer(1, unit="ns")

    # Expected 64-bit sign-extended value (two's complement of -42)
    # high 32 bits = all 1's, low 32 bits = 0xFFFFFFD6
    expected_bin = "11111111111111111111111111111111" + \
                   "11111111111111111111111111010110"   # 64 bits total
    expected_int_unsigned = (1 << 64) - 42   # unsigned 64-bit representation

    actual_int = int(dut.immediate.value)
    assert actual_int == expected_int_unsigned, \
           f"Integer mismatch: expected {expected_int_unsigned}, got {actual_int}"
    assert dut.immediate.value.signed_integer == -42, \
           f"Signed mismatch: expected -42, got {dut.immediate.value.signed_integer}"
    assert dut.immediate.value.binstr == expected_bin, \
           f"Binary mismatch:\n expected {expected_bin}\n got      {dut.immediate.value.binstr}"

@cocotb.test()
async def signext_s_type_test(dut):
    #100 randomized tests
    for _ in range(100):
        #TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111111111111111111111111)
        raw_data = imm # Just to keep the naming consistent
        source = 0b001
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns") #let it propagate...
        assert int(dut.immediate.value) == imm

        #TEST Negative IMM
        imm = random.randint(0b10000000000000000000000000000000,                      0b11111111111111111111111111111111) - (1 << 32)
        dut.raw_src.value = imm
        dut.imm_source.value = 0b001
        await Timer(1, unit="ns")
        result = int(dut.immediate.value)
        if result >= (1 << 63):
            result -= (1 << 64)
        assert result == imm

@cocotb.test()
async def signext_b_type_test(dut):
    #100 randomized tests
    for _ in range(100):
        #TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111111111111111111111111)
        raw_data = imm # Just to keep the naming consistent
        source = 0b010
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns") #let it propagate...
        assert int(dut.immediate.value) == imm

        #TEST Negative IMM
        imm = random.randint(0b10000000000000000000000000000000,                      0b11111111111111111111111111111111) - (1 << 32)
        dut.raw_src.value = imm
        dut.imm_source.value = 0b010
        await Timer(1, unit="ns")
        result = int(dut.immediate.value)
        if result >= (1 << 63):
            result -= (1 << 64)
        assert result == imm

@cocotb.test()
async def signext_j_type_test(dut):
    #100 randomized tests
    for _ in range(100):
        #TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111111111111111111111111)
        raw_data = imm # Just to keep the naming consistent
        source = 0b011
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns") #let it propagate...
        assert int(dut.immediate.value) == imm

        #TEST Negative IMM
        imm = random.randint(0b10000000000000000000000000000000,                      0b11111111111111111111111111111111) - (1 << 32)
        dut.raw_src.value = imm
        dut.imm_source.value = 0b011
        await Timer(1, unit="ns")
        result = int(dut.immediate.value)
        if result >= (1 << 63):
            result -= (1 << 64)
        assert result == imm

@cocotb.test()
async def signext_u_type_test(dut):
    #100 randomized tests
    for _ in range(100):
        #TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111111111111111111111111)
        Confirm = (imm << 32) # Just to keep the naming consistent
        source = 0b100
        await Timer(1, unit="ns")
        dut.raw_src.value = imm
        dut.imm_source.value = source
        await Timer(1, unit="ns")
        assert int(dut.immediate.value) == Confirm

