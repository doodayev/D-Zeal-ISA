import cocotb
from cocotb.triggers import Timer
import random



@cocotb.test()
async def add_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0000
    for _ in range(1000):
        src1 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        #We mask expected to not take account of overflows
        expected = (src1 + src2) & 0xFFFFFFFFFFFFFFFF
        #Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def default_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1111
    src1 = random.randint(0,0xFFFFFFFFFFFFFFFF)
    src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
    dut.src1.value = src1
    dut.src2.value = src2
    expected = 0
    #Await 1 ns for the infos to propagate
    await Timer(1, unit="ns")
    assert int(dut.alu_result.value) == expected

@cocotb.test()
async def zero_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0000
    dut.src1.value = 123
    dut.src2.value = -123
    await Timer(1, unit="ns")
    print(int(dut.alu_result.value))
    assert int(dut.zero.value) == 1
    assert int(dut.alu_result.value) == 0

@cocotb.test()
async def and_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0001
    for _ in range(1000):
        src1 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        #We mask expected to not take account of overflows
        expected = (src1 & src2)
        #Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def or_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0010
    for _ in range(1000):
        src1 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        #We mask expected to not take account of overflows
        expected = (src1 | src2)
        #Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def sub_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0011
    for _ in range(1000):
        src1 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        expected = (src1 - src2) & 0xFFFFFFFFFFFFFFFF

        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

    src1 = 0xF
    src2 = 0xE
    dut.src1.value = src1
    dut.src2.value = src2
    expected = (src1 - src2) & 0xFFFFFFFFFFFFFFFF
    await Timer(1, unit="ns")
    assert int(dut.alu_result.value) == expected

@cocotb.test()
async def slt_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0100
    def to_signed(x):
            return x if x < (1 << 63) else x - (1 << 64)
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        await Timer(1, unit="ns")
        expected = 1 if to_signed(src1) < to_signed(src2) else 0
        assert int(dut.alu_result.value) == expected
        # Optional: check that only LSB can be set
        assert dut.alu_result.value.binstr == ('0'*63 + str(expected))

@cocotb.test()
async def sltu_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0101
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = int(src1 < src2)

        assert dut.alu_result.value == 63*"0" + str(int(dut.alu_result.value))

@cocotb.test()
async def xor_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0110 #xor
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = src1 ^ src2

        assert int(dut.alu_result.value) == int(expected)

@cocotb.test()
async def sll_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0111
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        shamt = src2 & 0b111111
        dut.src2.value = shamt

        await Timer(1, unit="ns")
        expected = (src1 << shamt) & 0xFFFFFFFFFFFFFFFF

        assert int(dut.alu_result.value) == int(expected)

@cocotb.test()
async def srl_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1000
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        shamt = src2 & 0b111111
        dut.src2.value = shamt

        await Timer(1, unit="ns")
        expected = (src1 >> shamt) & 0xFFFFFFFFFFFFFFFF

        assert int(dut.alu_result.value) == int(expected)

#added for SRA
def arith_right_shift(x, shamt):
    """Return unsigned 64-bit result of arithmetic right shift of signed 64-bit value x by shamt bits."""
    shamt = shamt & 0x3F
    if shamt == 0:
        return x
    if x & (1 << 63):  # negative (MSB set)
        # Fill upper bits with 1
        return (x >> shamt) | ((0xFFFFFFFFFFFFFFFF << (64 - shamt)) & 0xFFFFFFFFFFFFFFFF)
    else:
        return x >> shamt

@cocotb.test()
async def sra_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1001
    for _ in range(1000):
        #UNSIGNED TESTS
        src1 = random.randint(0,0x7FFFFFFFFFFFFFFF) #because "unsigned"
        src2 = random.randint(0,0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        shamt = src2 & 0b111111
        dut.src2.value = shamt

        await Timer(1, unit="ns")
        expected = (src1 >> shamt) & 0xFFFFFFFFFFFFFFFF

        assert int(dut.alu_result.value) == int(expected)

        # SIGNED TESTS
        src1 = random.randint(0x8000000000000000, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        shamt = src2 & 0b111111
        dut.src2.value = shamt

        await Timer(1, unit="ns")
        expected = arith_right_shift(src1, shamt)
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def last_bit_test(dut):
    # (logic copy-pasted from slt_test function)
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0100
    def to_signed(x):
            return x if x < (1 << 63) else x - (1 << 64)
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        await Timer(1, unit="ns")
        expected = 1 if to_signed(src1) < to_signed(src2) else 0
        assert int(dut.alu_result.value) == expected
        # Optional: check that only LSB can be set
        assert dut.alu_result.value.binstr == ('0'*63 + str(expected))

        assert dut.last_bit.value == str(expected)

@cocotb.test()
async def NE_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1010
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        await Timer(1, unit="ns")
        expected = 1 if src1 != src2 else 0
        assert int(dut.alu_result.value) == expected
        assert dut.alu_result.value.binstr == ('0'*63 + str(expected))
        assert dut.last_bit.value == str(expected)

@cocotb.test()
async def glt_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1011
    def to_signed(x):
            return x if x < (1 << 63) else x - (1 << 64)
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        await Timer(1, unit="ns")
        expected = 1 if to_signed(src1) > to_signed(src2) else 0
        assert int(dut.alu_result.value) == expected
        # Optional: check that only LSB can be set
        assert dut.alu_result.value.binstr == ('0'*63 + str(expected))

@cocotb.test()
async def gltu_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1100
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = int(src1 > src2)

        assert dut.alu_result.value == 63*"0" + str(int(dut.alu_result.value))
