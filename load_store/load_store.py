import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def ls_unit_test(dut):
    word = 0x726F626F746E6900

    # ====
    # StoreWorld (yeah THE WORLD) or StoreFull
    # ====
    dut.f4.value = 0b0100

    for _ in range(100):
        reg_data = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.reg_read.value = reg_data
        for offset in range(8):
            dut.alu_result_address.value = word | offset
            await Timer(1, unit="ns")
            assert dut.data.value == reg_data & 0xFFFFFFFFFFFFFFFF
            if offset == 0b000:
                assert dut.byte_enable.value == 0b11111111
            else :
                assert dut.byte_enable.value == 0b00000000
    # ====
    # StoreByte or StoreSquad or Steigth (Store+Eighth)
    # ====
    await Timer(10, unit="ns")

    dut.f4.value = 0b0000

    for _ in range(100):
        reg_data = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.reg_read.value = reg_data
        for offset in range(8):
            dut.alu_result_address.value = word | offset
            await Timer(1, unit="ns")
            if offset == 0b000:
                assert dut.byte_enable.value == 0b00000001
                assert dut.data.value == (reg_data & 0x00000000000000FF)
            elif offset == 0b001:
                assert dut.byte_enable.value == 0b00000010
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 8
            elif offset == 0b010:
                assert dut.byte_enable.value == 0b00000100
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 16
            elif offset == 0b011:
                assert dut.byte_enable.value == 0b00001000
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 24
            elif offset == 0b100:
                assert dut.byte_enable.value == 0b00010000
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 32
            elif offset == 0b101:
                assert dut.byte_enable.value == 0b00100000
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 40
            elif offset == 0b110:
                assert dut.byte_enable.value == 0b01000000
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 48
            elif offset == 0b111:
                assert dut.byte_enable.value == 0b10000000
                assert dut.data.value == (reg_data & 0x00000000000000FF) << 56

    # ===
    # StoreQuart or Squart (Store+quart) or StoreBrigade or Store2pac (2 byte... 2pac idk)
    # ===

    await Timer(10, unit="ns")

    dut.f4.value = 0b0001

    for _ in range(100):
        reg_data = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.reg_read.value = reg_data
        for offset in range(4):
            dut.alu_result_address.value = word | offset
            await Timer(1, unit="ns")
            if offset == 0b000:
                assert dut.byte_enable.value == 0b00000011
                assert dut.data.value == (reg_data & 0x000000000000FFFF)
            elif offset == 0b010:
                assert dut.byte_enable.value == 0b00001100
                assert dut.data.value == (reg_data & 0x000000000000FFFF) << 16
            elif offset == 0b100:
                assert dut.byte_enable.value == 0b00110000
                assert dut.data.value == (reg_data & 0x000000000000FFFF) << 32
            elif offset == 0b110:
                assert dut.byte_enable.value == 0b11000000
                assert dut.data.value == (reg_data & 0x000000000000FFFF) << 48
            else:
                assert dut.byte_enable.value == 0b00000000

    # ===
    # StoreChud or StoreChina or Stalf (Store+half)
    # ===

    await Timer(10, unit="ns")

    dut.f4.value = 0b0010

    for _ in range(100):
        reg_data = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.reg_read.value = reg_data
        for offset in range(4):
            dut.alu_result_address.value = word | offset
            await Timer(1, unit="ns")
            if offset == 0b000:
                assert dut.byte_enable.value == 0b00001111
                assert dut.data.value == (reg_data & 0x00000000FFFFFFFF)
            elif offset == 0b100:
                assert dut.byte_enable.value == 0b11110000
                assert dut.data.value == (reg_data & 0x00000000FFFFFFFF) << 32
            else:
                assert dut.byte_enable.value == 0b00000000
