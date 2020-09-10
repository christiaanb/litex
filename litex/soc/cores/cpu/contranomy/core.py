#
# This file is part of LiteX.
#
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Greg Davill <greg.davill@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex import get_data_mod
from litex.soc.interconnect import wishbone
from litex.soc.cores.cpu import CPU, CPU_GCC_TRIPLE_RISCV32


CPU_VARIANTS = ["standard"]


class Contranomy(CPU):
    name                 = "contranomy"
    human_name           = "Contranomy"
    variants             = CPU_VARIANTS
    data_width           = 32
    endianness           = "little"
    gcc_triple           = CPU_GCC_TRIPLE_RISCV32
    linker_output_format = "elf32-littleriscv"
    nop                  = "nop"
    io_regions           = {0x80000000: 0x80000000} # origin, length

    @property
    def gcc_flags(self):
        flags =  "-march=rv32i "
        flags += "-mabi=ilp32 "
        flags += "-D__contranomy__ "
        return flags

    def __init__(self, platform, variant="standard"):
        self.platform     = platform
        self.variant      = variant
        self.reset        = Signal()
        self.interrupt    = Signal(32)
        self.ibus         = ibus = wishbone.Interface()
        self.dbus         = dbus = wishbone.Interface()
        self.periph_buses = [ibus, dbus]
        self.memory_buses = []

        # # #

        self.cpu_params = dict(
            i_clk                   = ClockSignal(),
            i_reset                 = ResetSignal() | self.reset,

            i_externalInterrupt     = self.interrupt,
            i_timerInterrupt        = 0,
            i_softwareInterrupt     = 0,

            o_iBusWishbone_ADR      = self.ibus.adr,
            o_iBusWishbone_DAT_MOSI = self.ibus.dat_w,
            o_iBusWishbone_SEL      = self.ibus.sel,
            o_iBusWishbone_CYC      = self.ibus.cyc,
            o_iBusWishbone_STB      = self.ibus.stb,
            o_iBusWishbone_WE       = self.ibus.we,
            o_iBusWishbone_CTI      = self.ibus.cti,
            o_iBusWishbone_BTE      = self.ibus.bte,
            i_iBusWishbone_DAT_MISO = self.ibus.dat_r,
            i_iBusWishbone_ACK      = self.ibus.ack,
            i_iBusWishbone_ERR      = self.ibus.err,

            o_dBusWishbone_ADR      = self.dbus.adr,
            o_dBusWishbone_DAT_MOSI = self.dbus.dat_w,
            o_dBusWishbone_SEL      = self.dbus.sel,
            o_dBusWishbone_CYC      = self.dbus.cyc,
            o_dBusWishbone_STB      = self.dbus.stb,
            o_dBusWishbone_WE       = self.dbus.we,
            o_dBusWishbone_CTI      = self.dbus.cti,
            o_dBusWishbone_BTE      = self.dbus.bte,
            i_dBusWishbone_DAT_MISO = self.dbus.dat_r,
            i_dBusWishbone_ACK      = self.dbus.ack,
            i_dBusWishbone_ERR      = self.dbus.err,
        )

        # add verilog sources
        self.add_sources(platform)

    def set_reset_address(self, reset_address):
        assert not hasattr(self, "reset_address")
        self.reset_address = reset_address
        assert reset_address == 0x00000000, "cpu_reset_addr hardcoded to 0x000000000!"

    @staticmethod
    def add_sources(platform):
        vdir = get_data_mod("cpu", "contranomy").data_location
        platform.add_source_dir(os.path.join(vdir, "Contranomy", "contranomy"))
        platform.add_verilog_include_path(os.path.join(vdir, "Contranomy", "contranomy"))

    def do_finalize(self):
        assert hasattr(self, "reset_address")
        self.specials += Instance("contranomy", **self.cpu_params)
