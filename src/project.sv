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
  assign uo_out[7:1] = 7'b0;
  assign uio_out     = '0;
  assign uio_oe      = '0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:0], ui_in[7:1], 1'b0};

  // -----------------------------
  // Synchronous reset generation
  // -----------------------------
  reg [1:0] rst_sync;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      rst_sync <= 2'b11;       // force reset initially
    else
      rst_sync <= {rst_sync[0], 1'b0}; // shift in 0 to de-assert reset
  end
  wire rst_sync_n = ~rst_sync[1]; // active high synchronous reset

  control control_u (
    .clk(clk),
    .rst_n(rst_sync_n),        // use synchronized reset
    .rx_serial(ui_in[0]),
    .tx_serial(uo_out[0])
  );

endmodule