# Custom config for EE748 Assignment 2
# Yashas M Salian (yashas.msalian@iitb.ac.in)

import sys

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.utils.requires import requires
from gem5.resources.resource import BinaryResource
from gem5.resources.resource import FileResource
from m5.stats import *

from switchable_cpu import CustomSwitchableProcessor
from cache_hierarchy import CustomCacheHierarchy

requires(isa_required=ISA.X86)

# Adding a processor
processor = CustomSwitchableProcessor(num_cores=1, isa=ISA.X86, fastforward_insts=int(sys.argv[1]), warmup_insts=int(sys.argv[2]), detailed_insts=int(sys.argv[3]))

# Adding a custom cache hierarchy
cache_hierarchy = CustomCacheHierarchy(l1d_size="32kB", l1i_size="32kB", l2_size="256kB")

# Adding memory
memory = SingleChannelDDR3_1600(size="4GB")

# Setting up simple board for SE simulation
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Setting program arguments and workload
prog_args = []
if len(sys.argv) > 5:
    for argnum in range(5, len(sys.argv)):
        prog_args.append(sys.argv[argnum].strip('"'))
board.set_se_binary_workload(binary=BinaryResource(local_path=sys.argv[4]), arguments=prog_args)

# Some convenient functions to be run at transition points
def switch_cpu() -> bool:
    processor.switch()
    print("Switching to detailed CPU for warmup")
    return False

def complete_warmup() -> bool:
    processor.switch()
    m5.stats.reset()
    print("Entering region of interest")
    return False

# Setup and run the simulator
simulator = Simulator(board=board, on_exit_event={ExitEvent.MAX_INSTS:[switch_cpu, complete_warmup]})
simulator.run()

print(
    "Exiting @ tick {} because {}.".format(
        simulator.get_current_tick(), simulator.get_last_exit_event_cause()
    )
)
