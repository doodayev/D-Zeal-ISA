#Makefile

#defaults
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/cpu.sv
#use VHDL_SOURCES for VHDL files

#COCOTB_TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
COCOTB_TOPLEVEL = cpu

#COCOTB_TEST_MODULES is the basename of the Python test file(s)
COCOTB_TEST_MODULES = test_cpu

#Enable waves
WAVES=1
GUI=1 #Setting to 1 for vcddiff GUI

#Adding flags for tracing
EXTRA_ARGS += --trace --trace-structs

#include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim


