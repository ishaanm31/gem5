# Custom configuration for Switchable CPU
# Yashas M Salian (yashas.msalian@iitb.ac.in)

from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.isas import ISA
from gem5.utils.override import *
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.boards.mem_mode import MemMode
from gem5.components.processors.cpu_types import get_mem_mode
from core import X86_O3_Custom
from m5.objects import *
from m5.util import fatal

class CustomSwitchableProcessor(SwitchableProcessor):
    def __init__(
        self,
        num_cores: int,
        fastforward_insts: int,
        warmup_insts: int,
        detailed_insts: int,
        isa: ISA = None,
    ) -> None:
        """
        :param isa: The ISA of the processor.
        """

        if num_cores <= 0:
            raise AssertionError("Number of cores must be a positive integer!")

        self._start_key = "start"
        self._switch_key1 = "switch1"
        self._switch_key2 = "switch2"
        self._current_is_start = True
        self._current_is_switch1 = False

        # Starting Cache mode for KVM CPU
        self._mem_mode = MemMode.ATOMIC_NONCACHING

        switchable_cores = {
            self._start_key: [
                BaseCPUCore(core=X86KvmCPU(cpu_id=i, max_insts_any_thread=fastforward_insts), isa=isa)
                for i in range(num_cores)
            ],
            self._switch_key1: [
                BaseCPUCore(core=X86TimingSimpleCPU(cpu_id=i, max_insts_any_thread=warmup_insts), isa=isa)
                for i in range(num_cores)
            ],
            self._switch_key2: [
                BaseCPUCore(core=X86_O3_Custom(cpu_id=i, max_insts_any_thread=detailed_insts), isa=isa)
                for i in range(num_cores)
            ],
        }

        super().__init__(
            switchable_cores=switchable_cores, starting_cores=self._start_key
        )

    @overrides(SwitchableProcessor)
    def incorporate_processor(self, board: AbstractBoard) -> None:
        super().incorporate_processor(board=board)

        if (
            board.get_cache_hierarchy().is_ruby()
            and self._mem_mode == MemMode.ATOMIC
        ):
            warn(
                "Using an atomic core with Ruby will result in "
                "'atomic_noncaching' memory mode. This will skip caching "
                "completely."
            )
            self._mem_mode = MemMode.ATOMIC_NONCACHING
        board.set_mem_mode(self._mem_mode)

    def switch(self):
        """Switches to the "switched out" cores."""
        if self._current_is_start:
            self.switch_to_processor(self._switch_key1)
            self._current_is_start = False
            self._current_is_switch1 = True
        elif self._current_is_switch1:
            self.switch_to_processor(self._switch_key2)
            self._current_is_switch1 = False
        else:
            fatal("No CPU available to switch to")
