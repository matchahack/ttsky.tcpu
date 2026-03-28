/*
 * Copyright (c) 2026 Kai Harris
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_tcpu_alienflip (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out[7:5] = 'b0;
  assign uo_out[3:0] = 'b0;
  assign uio_out     = '0;
  assign uio_oe      = '0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:0], ui_in[7:4], ui_in[2:0], 1'b0};

  // CLKS_PER_BIT = (Frequency of i_Clock)/(Frequency of UART)
  //// 50 MHz Clock, 115200 baud UART
  //// (50000000)/(115200)  = 434
  parameter CLKS_PER_BIT = 434;

  // -----------------------------
  // Synchronous reset generation
  // -----------------------------
  wire rst_sync;
  sync_reset sync_reset_u (
      .clk(clk),
      .rst_n(rst_n),
      .rst_sync(rst_sync)
  );

  base_interface #(
      .CLKS_PER_BIT(CLKS_PER_BIT)
  ) base_interface_u (
      .clk(clk),
      .rst_n(rst_n),
      .rx_serial_i(ui_in[3:3]),
      .tx_serial_o(uo_out[4:4])
  );

endmodule