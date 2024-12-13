import sys
import argparse
from pathlib import Path

# from ...src.python.gem5.components.boards.simple_board import SimpleBoard
# from ...src.python.gem5.components.boards.simple_board import SimpleBoard
# from ...src.python.gem5.components.memory import SingleChannelDDR3_1600
# from ...src.python.gem5.components.processors.cpu_types import CPUTypes
# from ...src.python.gem5.isas import ISA
# from ...src.python.gem5.resources.resource import obtain_resource
# from ...src.python.gem5.simulate.simulator import Simulator
# from ...src.python.gem5.simulate.exit_event import ExitEvent
# from ...src.python.gem5.utils.requires import requires
# from ...src.python.gem5.resources.resource import BinaryResource
# from ...src.python.gem5.resources.resource import FileResource
# from ...src.python.m5.stats import *

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.resources.resource import FileResource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.utils.requires import requires
from m5.stats import reset

import spec06_benchmarks  # Import SPEC2006 benchmark definitions
from switchable_cpu import CustomSwitchableProcessor
from cache_hierarchy import CustomCacheHierarchy

# Argument parser for simulation settings
parser = argparse.ArgumentParser(description="Run SPEC CPU2006 benchmarks on gem5.")

parser.add_argument(
    "-f", "--fast-forward",
    type=int,
    default=0,
    help="Number of fast-forward instructions.",
)
parser.add_argument(
    "-w", "--warmup-insts",
    type=int,
    default=0,
    help="Number of warmup instructions.",
)
parser.add_argument(
    "-m", "--maxinsts",
    type=int,
    default=1000000,
    help="Number of instructions for detailed simulation.",
)
parser.add_argument(
    "-b", "--benchmark",
    type=str,
    required=True,
    help="The SPEC benchmark to be loaded (e.g., 'perlbench', 'bzip2').",
)
parser.add_argument(
    "--benchmark_stdout",
    type=str,
    default="benchmark.out",
    help="Path for stdout redirection for the benchmark.",
)
parser.add_argument(
    "--benchmark_stderr",
    type=str,
    default="benchmark.err",
    help="Path for stderr redirection for the benchmark.",
)

args = parser.parse_args()

# Ensure the ISA and required features are met
requires(isa_required=ISA.X86, kvm_required=True)

# Retrieve the benchmark process
if args.benchmark:
    print(f"Selected SPEC_CPU2006 benchmark: {args.benchmark}")
    try:
        # process = getattr(spec06_benchmarks, args.benchmark)
        process = spec06_benchmarks.benchmarks[args.benchmark]
    except :
        print(f"Error: Benchmark '{args.benchmark}' is not recognized.")
        sys.exit(1)
else:
    print("Error: No benchmark specified. Use the '--benchmark' argument.")
    sys.exit(1)

# Set stdout and stderr for the process
output = args.benchmark_stdout
errout = args.benchmark_stderr
print(f"Benchmark stdout redirected to: {output}")
print(f"Benchmark stderr redirected to: {errout}")

# Create the processor
processor = CustomSwitchableProcessor(
    num_cores=1,
    isa=ISA.X86,
    fastforward_insts=args.fast_forward,
    warmup_insts=args.warmup_insts,
    detailed_insts=args.maxinsts,
)

# Create the cache hierarchy
cache_hierarchy = CustomCacheHierarchy(
    l1d_size="32kB",
    l1i_size="32kB",
    l2_size="256kB",
)

# Set up the memory
memory = SingleChannelDDR3_1600(size="4GB")

# Create the board
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Configure the binary workload
if "input" in process:
    board.set_se_binary_workload(
        binary=BinaryResource(process['executable']),
        arguments=process['cmd'][1:],
        stdout_file=Path(output),
        stderr_file=Path(errout),
        stdin_file=FileResource(process["input"])
    )
else:
    board.set_se_binary_workload(
        binary=BinaryResource(process['executable']),
        arguments=process['cmd'][1:],
        stdout_file=Path(output),
        stderr_file=Path(errout),
    )

# Define simulation events
def switch_cpu() -> bool:
    processor.switch()
    print("Switching to detailed CPU for warmup.")
    return False

def complete_warmup() -> bool:
    processor.switch()
    reset()
    print("Entering region of interest.")
    return False

# Create and run the simulator
simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.MAX_INSTS: [switch_cpu, complete_warmup],
    },
)

print(f"Running benchmark: {args.benchmark}")
simulator.run()

print(
    f"Exiting @ tick {simulator.get_current_tick()} because "
    f"{simulator.get_last_exit_event_cause()}."
)
