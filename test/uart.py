# SPDX-FileCopyrightText: © 2024 Kai Harris
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotbext.uart import UartSource, UartSink
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
import logging

logging.basicConfig(level=logging.DEBUG)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLK_PERIOD_NS = 100 # 10 MHz
RESET_CYCLES  = 10000
SETTLE_CYCLES = int(1e5)
BAUD_RATE     = 115200
UART_BITS     = 8

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def reset_dut(dut):
    """Assert then deassert active-low reset."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    dut._log.info("Reset")
    dut.rst_n.value = 0
    dut.uo_out.value = 0
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)

async def run_program(dut, bytes_: list[int], description: str):
    """Upload *bytes_* over UART, wait for the result, and log data_in/data_out."""
    await reset_dut(dut)
    uart_source = UartSource(dut.uart_rx, baud=BAUD_RATE, bits=UART_BITS)
    uart_sink   = UartSink(dut.uart_tx,   baud=BAUD_RATE, bits=UART_BITS)
    
    dut._log.info(f"\nRunning program: {description}")
    await uart_source.write(bytes_)
    await uart_source.wait()
    for i in range(SETTLE_CYCLES):
        await RisingEdge(dut.clk)
        dut.uo_out.value = f'0000000{dut.uart_tx}'
    await uart_sink.read(7)
