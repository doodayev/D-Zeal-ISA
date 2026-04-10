#memory.py

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def reset(dut):
    await RisingEdge(dut.clk)
    dut. rst_n.value = 0
    dut.write_enable.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    #Assert all is 0 after reset
    for address in range(dut.WORDS.value):
        dut.address.value = address
        await Timer(1, unit="ns")
        #just 64 zeroes
        assert dut.read_data.value == "0000000000000000000000000000000000000000000000000000000000000000"

@cocotb.test()
async def memory_data_test(dut):
    #Start a 10ns clock
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    await reset(dut)

    #Test: Write and read back data
    test_data = [
            (0, 0x8008135580081355),
            (8, 0xC99CD99DE99EA99A),
            (16,0x2242574222425742),
            (24,0x8086650280866502)
    ]

    #For the first tests, we will deal with word operations
    dut.byte_enable.value = 0b11111111

    # ========================
    # BASIC WORD WRITE TEST
    # ========================

    for address, data in test_data:
        dut.address.value = address
        dut.write_data.value = data

        #write
        dut.write_enable.value = 1
        await RisingEdge(dut.clk)
        dut.write_enable.value = 0
        await RisingEdge(dut.clk)

        #Verify by reading back
        dut.address.value = address
        await RisingEdge(dut.clk)
        assert dut.read_data.value == data, f"Error at address {address}: expected {hex(data)}, got {hex(dut.read_data.value)}"

    # ==============
    # WRITE TEST #2
    # ==============

    for i in range(40, 4):
        dut.address.value = i
        dut.write_data.value = i
        dut.write_enable.value = 1
        await RisingEdge(dut.clk)

    # =================
    # NO WRITE TEST
    # =================

    dut.write_enable.value = 0
    for i in range(40, 4):
        dut.address.value = i
        await RisingEdge(dut.clk)
        expected_value = i
        assert dut.read_data.value == expected_value, f"Expected {expected_value}, got {dut.read_data.value} at address {i}"

    # ==================
    # BYTE WRITE TEST
    # ==================
    dut.write_enable.value = 1

    for byte_enable in range(32):
        await reset(dut) #reset memory
        dut.byte_enable.value = byte_enable
        #generate mask from byte_enable
        mask = 0
        for j in range(8):
            if (byte_enable >> j) & 1:
                mask |= (0xFF << (j*8))

        for address, data in test_data:
            dut.address.value = address
            dut.write_data.value = data

            #write
            dut.write_enable.value = 1
            await RisingEdge(dut.clk)
            dut.write_enable.value = 0
            await RisingEdge(dut.clk)

            #Verify by reading back
            await RisingEdge(dut.clk)
