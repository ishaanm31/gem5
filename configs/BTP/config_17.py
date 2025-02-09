import sys
import argparse
from pathlib import Path
import subprocess

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.utils.requires import requires
from m5.stats import reset

from switchable_cpu import CustomSwitchableProcessor
from cache_hierarchy import CustomCacheHierarchy

# Argument parser for simulation settings
parser = argparse.ArgumentParser(description="Run SPEC CPU2017 benchmarks on gem5.")

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
    help="The SPEC CPU2017 benchmark to be executed (e.g., '500.perlbench_r').",
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

# Run runcpu to get the correct command for the benchmark
try:
    spec_dir = "/home/ishaan/distrobox_ubuntu22/spec2017"
    runcpu_cmd = [
        f"{spec_dir}/bin/runcpu",
        "--config=myconfig",
        "--action=onlyrun",
        "--noreportable",
        args.benchmark
    ]

    # Get the runcpu command that should be executed
    result = subprocess.run(runcpu_cmd, capture_output=True, text=True, check=True)
    command = result.stdout.strip().split("\n")[-1]  # Extract last line as command
    print(f"Executing benchmark command: {command}")

except subprocess.CalledProcessError as e:
    print(f"Error executing runcpu: {e}")
    sys.exit(1)

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

# Configure the binary workload using the extracted command
board.set_se_binary_workload(
    binary=command.split()[0],  # Extract the executable
    arguments=command.split()[1:],  # Extract the arguments
    stdout_file=Path(args.benchmark_stdout),
    stderr_file=Path(args.benchmark_stderr),
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
