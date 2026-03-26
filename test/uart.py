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
    dut.ena.value = 1
    dut.uo_out.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)

async def run_program(dut, bytes_: list[int], description: str):
    """Upload *bytes_* over UART, wait for the result, and log data."""
    await reset_dut(dut)
    dut.uart_rx.value = 1
    await RisingEdge(dut.clk)

    uart_source = UartSource(dut.uart_rx, baud=BAUD_RATE, bits=UART_BITS)
    uart_sink   = UartSink(
        dut.uart_tx,
        baud=BAUD_RATE,
        bits=UART_BITS
    )

    dut._log.info(f"\nRunning program: {description}")
    dut._log.info(f"Sending {len(bytes_)} bytes: {bytes_}")

    # Send program
    await uart_source.write(bytes_)
    await uart_source.wait()
    dut._log.info("UART write complete")

    # Debug: track TX changes
    last_tx = None

    for cycle in range(SETTLE_CYCLES):
        await RisingEdge(dut.clk)

        # Log TX transitions (helps see if UART is alive)
        tx_val = str(dut.uart_tx.value)

        if tx_val != last_tx:
            dut._log.debug(f"[cycle {cycle}] uart_tx changed -> {tx_val}")
            last_tx = tx_val

        # Log when bytes arrive
        if uart_sink.count() > 0:
            dut._log.debug(
                f"[cycle {cycle}] RX count = {uart_sink.count()}"
            )

        # Exit when enough data
        if uart_sink.count() >= 7:
            dut._log.info(f"Received 7 bytes after {cycle} cycles")
            break
    else:
        # Timeout diagnostics
        dut._log.error("Timeout waiting for UART data")
        dut._log.error(f"Bytes received: {uart_sink.count()}")

        # Try to dump partial data if any
        partial = []
        while uart_sink.count() > 0:
            partial.append(uart_sink.read_nowait(1)[0])

        dut._log.error(f"Partial data: {partial}")
        raise RuntimeError("UART timeout")

    # Read final data
    data = uart_sink.read_nowait(7)
    dut._log.info(f"Final received data: {data}")

    return data