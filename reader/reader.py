# test_reader.py

import cocotb
from cocotb.triggers import Timer
import random

#100 random test per mask

@cocotb.test()
async def reader_world_test(dut):
    #WORLD TEST CASE
    dut.f4.value = 0b0100
    await Timer(1, unit="ns")
    dut.byteMask.value = 0b11111111
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == mem_data

@cocotb.test()
async def reader_invalid_test(dut):
    dut.f4.value = 0b0001
    dut.mem_data.value = random.randint(0,0xFFFFFFFFFFFFFFFF)
    for i in range(256):
        dut.byteMask.value = i
        await Timer(1, unit="ns")
        if i == 0:
            assert dut.valid.value == 0
        else :
            assert dut.valid.value == 1

@cocotb.test()
async def reader_brigade_test(dut):
    #BRIGADE TEST
    dut.f4.value = 0b0001

    await Timer(1, unit="ns")

    dut.byteMask.value = 0b11000000
    await Timer(1, unit="ns")
    for _ in range(100):
        #UNSIGNED
        mem_data = random.randint(0,0x7FFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0xFFFF000000000000) >> 48;
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x8000000000000000,0xFFFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0xFFFF000000000000) >> 48) - (1 << 16)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00110000
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        # Add a random AEAE to check if they are ignored
        mem_data = random.randint(0,0x00007FFFFFFFFFFF) | 0xAEAE000000000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x0000FFFF00000000) >> 32
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000800000000000,0x0000FFFFFFFFFFFF) | 0xAEAE000000000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x0000FFFF00000000) >> 32) - (1 << 16)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00001100
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0,0x000000007FFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x00000000FFFF0000) >> 16
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000080000000,0x00000000FFFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x00000000FFFF0000) >> 16) - (1 << 16)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00000011
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0,0x0000000000007FFF) | 0xAEAEAEAEAEAE0000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x000000000000FFFF)
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000000008000,0x000000000000FFFF) | 0xAEAEAEAEAEAE0000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x000000000000FFFF)) - (1 << 16)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

@cocotb.test()
async def reader_squad_test(dut):
    #BYTE TEST
    dut.f4.value = 0b0000

    await Timer(1, unit="ns")

    dut.byteMask.value = 0b10000000
    await Timer(1, unit="ns")
    for _ in range(100):
        #UNSIGNED
        mem_data = random.randint(0,0x7FFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0xFF00000000000000) >> 56
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x8000000000000000,0xFFFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0xFF00000000000000) >> 56) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b01000000
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x007FFFFFFFFFFFFF) | 0xAE00000000000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x00FF000000000000) >> 48
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0080000000000000,0x00FFFFFFFFFFFFFF) | 0xAE00000000000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x00FF000000000000) >> 48) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00100000
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x00007FFFFFFFFFFF) | 0xAEAE000000000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x0000FF0000000000) >> 40
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000800000000000,0x0000FFFFFFFFFFFF) | 0xAEAE000000000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x0000FF0000000000) >> 40) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00010000
    await Timer(1, unit="ns")
    for _ in range(100):
        #UNSIGNED
        mem_data = random.randint(0,0x0000007FFFFFFFFF) | 0xAEAEAE0000000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x000000FF00000000) >> 32
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000008000000000,0x000000FFFFFFFFFF) | 0xAEAEAE0000000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x000000FF00000000) >> 32) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00001000
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x000000007FFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x00000000FF000000) >> 24
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000080000000,0x00000000FFFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x00000000FF000000) >> 24) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00000100
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x00000000007FFFFF) | 0xAEAEAEAEAE000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x0000000000FF0000) >> 16
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000000800000,0x0000000000FFFFFF) | 0xAEAEAEAEAE000000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x0000000000FF0000) >> 16) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00000010
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x0000000000007FFF) | 0xAEAEAEAEAEAE0000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x000000000000FF00) >> 8
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000000008000,0x000000000000FFFF) | 0xAEAEAEAEAEAE0000
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0x000000000000FF00) >> 8) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    dut.byteMask.value = 0b00000001
    await Timer(1, unit="ns")
    for _ in range(100):
        # UNSIGNED
        mem_data = random.randint(0,0x000000000000007F) | 0xAEAEAEAEAEAEAE00
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x00000000000000FF)
        assert dut.valid.value == 1

        #SIGNED
        mem_data = random.randint(0x0000000000000080,0x00000000000000FF) | 0xAEAEAEAEAEAEAE00
        dut.mem_data.value = mem_data
        expected = (mem_data & 0x00000000000000FF) - (1 << 8)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

@cocotb.test()
async def reader_StoreHalf_test(dut):
    # ==========================================
    # LOWER 32-BIT HALF-WORD TESTS
    # ==========================================
    dut.byteMask.value = 0b00001111
    await Timer(1, unit="ns")

    # UNSIGNED
    dut.f4.value = 0b1010  # 0b1010 means f4[3]=1, which is UNSIGNED
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0, 0xFFFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0x00000000FFFFFFFF)
        assert dut.valid.value == 1

    # SIGNED
    dut.f4.value = 0b0010  # 0b0010 means f4[3]=0, which is SIGNED
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0x0000000080000000, 0x00000000FFFFFFFF) | 0xAEAEAEAE00000000
        dut.mem_data.value = mem_data
        expected = (mem_data & 0x00000000FFFFFFFF) - (1 << 32)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1

    # ==========================================
    # UPPER 32-BIT HALF-WORD TESTS
    # ==========================================
    dut.byteMask.value = 0b11110000
    await Timer(1, unit="ns")

    # UNSIGNED
    dut.f4.value = 0b1010  # UNSIGNED
    await Timer(1, unit="ns")
    for _ in range(100):
        # We can use the full range here because the hardware will mask and zero-extend it
        mem_data = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        await Timer(1, unit="ns")
        assert dut.writeBack.value == (mem_data & 0xFFFFFFFF00000000) >> 32
        assert dut.valid.value == 1

    # SIGNED
    dut.f4.value = 0b0010  # SIGNED
    await Timer(1, unit="ns")
    for _ in range(100):
        mem_data = random.randint(0x8000000000000000, 0xFFFFFFFFFFFFFFFF)
        dut.mem_data.value = mem_data
        expected = ((mem_data & 0xFFFFFFFF00000000) >> 32) - (1 << 32)
        await Timer(1, unit="ns")
        assert int(dut.writeBack.value) - (1 << 64) == expected
        assert dut.valid.value == 1
