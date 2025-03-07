import m5
from m5.objects import Process

# Dictionary containing all SPEC CPU2006 benchmarks
benchmarks = {
    "astar": {
        "executable": "astar",
        "cmd": ["astar", "BigLakes2048.cfg"],
    },
    "bzip2": {
        "executable": "bzip2",
        "cmd": ["bzip2", "input.program"],
    },
    "bwaves_r": {
        "executable": "bwaves_r",
        "cmd": ["bwaves_r", "<", "../../data/refrate/input/bwaves_1.in"]
    },
    "cactusADM": { #NotWorking
        "executable": "cactusADM",
        "cmd": ["cactusADM", "cactusADM", "benchADM.par"],
    },
    "cactuBSSN_r": {
        "executable": "cactusBSSN_r",
        "cmd": ["cactusBSSN_r", "spec_ref.par"],
    },    
    "mcf_r": {
        "executable": "mcf_r",
        "cmd": ["mcf_r", "inp.in"],
    },
    "calculix": {
        "executable": "calculix",
        "cmd": ["calculix", "hyperviscoplastic"],
    },
    "dealII": {
        "executable": "dealII",
        "cmd": ["dealII", "100"],
    },
    "gamess": { #NotWorking
        "executable": "gamess",
        "cmd": ["gamess"],
        "input": "cytosine.2.config",
    },
    "gcc_r": {
        "executable": "cpugcc_r",
        "cmd": ["cpugcc_r", "../../run/run_base_refrate_mytest-m64.0000/gcc-smaller.c"],
    },
    "GemsFDTD": { #NotWorking
        "executable": "GemsFDTD",
        "cmd": ["GemsFDTD"],
    },
    "gobmk": {
        "executable": "gobmk",
        "cmd": ["gobmk", "--quiet", "--mode", "gtp"],
        "input": "13x13.tst",
    },
    "gromacs": {
        "executable": "gromacs",
        "cmd": ["gromacs", "-silent", "-deffnm", "gromacs", "-nice", "0"],
    },
    "h264ref": {
        "executable": "h264ref",
        "cmd": ["h264ref"],
    },
    "hmmer": {
        "executable": "hmmer",
        "cmd": ["hmmer", "nph3.hmm"],
    },
    "lbm": {
        "executable": "lbm",
        "cmd": ["lbm", "3000", "reference.dat", "0", "0", "100_100_130_ldc.of"],
    },
    "leslie3d": { #NotWorking
        "executable": "leslie3d",
        "cmd": ["leslie3d"],
        "input": "leslie3d.in",
    },
    "libquantum": {
        "executable": "libquantum",
        "cmd": ["libquantum", "1397", "8"],
    },
    "mcf": {
        "executable": "mcf",
        "cmd": ["mcf", "inp.in"],
    },
    "milc": {
        "executable": "milc",
        "cmd": ["milc"],
        "input": "su3imp.in",
    },
    "namd": {
        "executable": "namd",
        "cmd": ["namd", "--input", "namd.input", "--iterations", "38"],
    },
    "omnetpp": {
        "executable": "omnetpp",
        "cmd": ["omnetpp"],
    },
    "perlbench": {
        "executable": "perlbench",
        "cmd": ["perlbench", "splitmail.pl", "1600", "12", "26", "16", "4500"],
    },
        "perlbench_r": {
        "executable": "perlbench_r",
        "cmd": ["perlbench_r", "-I./lib", "-e", 'print "Hello, SPEC!\n";']
    },
    "povray": {
        "executable": "povray",
        "cmd": ["povray", "SPEC-benchmark-ref.ini"],
    },
    "sjeng": {
        "executable": "sjeng",
        "cmd": ["sjeng", "ref.txt"],
    },
    "soplex": {
        "executable": "soplex",
        "cmd": ["soplex", "pds-50.mps"],
    },
    "sphinx3": {
        "executable": "sphinx_livepretend",
        "cmd": ["sphinx_livepretend", "ctlfile", ".", "args.an4"],
    },
    "specrand_f": {
        "executable": "specrand",
        "cmd": ["specrand", "1255432124", "234923"],
    },
    "tonto": { #NotWorking
        "executable": "tonto",
        "cmd": ["tonto"],
    },
    "wrf": { #NotWorking
        "executable": "wrf",
        "cmd": ["wrf"],
    },
    "Xalan": {
        "executable": "Xalan",
        "cmd": ["Xalan", "t5.xml", "xalanc.xsl"],
    },
    "zeusmp": { #NotWorking
        "executable": "zeusmp",
        "cmd": ["zeusmp"],
    },
}

# Function to get a Process object from the dictionary
def get_benchmark_process(benchmark_name):
    if benchmark_name not in benchmarks:
        raise ValueError(f"Benchmark '{benchmark_name}' is not defined.")
    
    benchmark = benchmarks[benchmark_name]
    process = Process()
    process.executable = benchmark["executable"]
    process.cmd = benchmark["cmd"]
    if "input" in benchmark:
        process.input = benchmark["input"]
    return process

# Example usage
if __name__ == "__main__":
    # Replace with the desired benchmark
    benchmark_name = "lbm"  # e.g., "perlbench", "gcc", etc.
    
    # Retrieve the process for the selected benchmark
    try:
        process = get_benchmark_process(benchmark_name)
        print(f"Running benchmark: {benchmark_name}")
        print(f"Executable: {process.executable}")
        print(f"Command: {process.cmd}")
        if hasattr(process, "input"):
            print(f"Input: {process.input}")
    except ValueError as e:
        print(e)
