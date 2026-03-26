/*
 * Copyright (c) 2026 Kai Harris
 * SPDX-License-Identifier: Apache-2.0
 */
 
module control (
    input   logic clk,
    input   logic rst_n,
    input   logic rx_serial,
    output  logic tx_serial
);

// Set Parameter CLKS_PER_BIT as follows:
// CLKS_PER_BIT = (Frequency of i_Clock)/(Frequency of UART)
// Example: 25 MHz Clock, 115200 baud UART
// (25000000)/(115200)  = 217
// (50000000)/(115200)  = 434
// (10000000)/(115200)  = 86
// (10000000)/(9600)  = 86 
parameter CLKS_PER_BIT = 1041;

base_interface #(
    .CLKS_PER_BIT(CLKS_PER_BIT)
) base_interface_u (
    .clock(clk),
    .nreset(rst_n),
    .rx_serial_i(rx_serial),
    .tx_serial_o(tx_serial)
);

endmodule