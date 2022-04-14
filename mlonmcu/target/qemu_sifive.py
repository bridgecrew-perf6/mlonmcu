#
# Copyright (c) 2022 TUM Department of Electrical and Computer Engineering.
#
# This file is part of MLonMCU.
# See https://github.com/tum-ei-eda/mlonmcu.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""MLonMCU Qemu Sifive Target definitions"""

import os
import re
import csv
from pathlib import Path

from mlonmcu.logging import get_logger
from .common import cli, execute
from .riscv import RISCVTarget
from .metrics import Metrics

logger = get_logger()

# TODO: create (Riscv)QemuTarget with variable machine

class QemuSifiveTarget(RISCVTarget):
    """Target using a sifive_u machine in the QEMU simulator"""

    FEATURES = []

    DEFAULTS = {
        **RISCVTarget.DEFAULTS,
    }
    REQUIRED = RISCVTarget.REQUIRED + ["riscv32_qemu.exe"]

    def __init__(self, name="qemu_sifive", features=None, config=None):
        super().__init__(name, features=features, config=config)

    @property
    def riscv32_qemu_exe(self):
        return self.config["riscv32_qemu.exe"]

    def get_qemu_args(self, program):
        args = []
        args.extend(["-machine", "sifive_u"])
        args.append("-nographic")
        args.extend(["-kernel", program])
        return args

    def exec(self, program, *args, cwd=os.getcwd(), **kwargs):
        """Use target to execute a executable with given arguments"""
        assert len(args) == 0, "Qemu does not support passing arguments."
        qemu_args = self.get_qemu_args(program)

        if self.timeout_sec > 0:
            raise NotImplementedError
        else:
            ret = execute(
                self.riscv32_qemu_exe,
                *qemu_args,
                cwd=cwd,
                **kwargs,
            )
        return ret

    def parse_stdout(self, out, handle_exit=None):
        cycles = 0
        # exit_match = re.search(r"exit called with code: (.*)", out)
        # if exit_match:
        #     exit_code = int(exit_match.group(1))
        #     if handle_exit is not None:
        #         exit_code = handle_exit(exit_code)
        #     if exit_code != 0:
        #         logger.error("Execution failed - " + out)
        #         raise RuntimeError(f"unexpected exit code: {exit_code}")
        # error_match = re.search(r"ETISS: Error: (.*)", out)
        # if error_match:
        #     error_msg = error_match.group(1)
        #     raise RuntimeError(f"An ETISS Error occured during simulation: {error_msg}")

        # cpu_cycles = re.search(r"CPU Cycles \(estimated\): (.*)", out)
        # if not cpu_cycles:
        #     logger.warning("unexpected script output (cycles)")
        #     cycles = None
        # else:
        #     cycles = int(float(cpu_cycles.group(1)))
        # mips_match = re.search(r"MIPS \(estimated\): (.*)", out)
        # if not mips_match:
        #     raise logger.warning("unexpected script output (mips)")
        #     mips = None
        # else:
        #     mips = int(float(mips_match.group(1)))

        return cycles

    def get_metrics(self, elf, directory, handle_exit=None):
        out = ""

        if self.print_outputs:
            out += self.exec(elf, cwd=directory, live=True, handle_exit=handle_exit)
        else:
            out += self.exec(
                elf, cwd=directory, live=False, print_func=lambda *args, **kwargs: None, handle_exit=handle_exit
            )
        total_cycles = self.parse_stdout(out, handle_exit=handle_exit)

        metrics = Metrics()
        metrics.add("Total Cycles", total_cycles)

        return metrics, out

    def get_target_system(self):
        return self.name

    def get_platform_defs(self, platform):
        assert platform == "mlif"
        ret = super().get_platform_defs(platform)
        return ret


if __name__ == "__main__":
    cli(target=QemuSifiveTarget)
