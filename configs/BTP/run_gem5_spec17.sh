#!/bin/bash
start=$(date +%s)
SECONDS=0

while getopts ":b:o:f:w:m:e:branchoutcomefile:-:" flag
do
    case "${flag}" in
        b) BENCHMARK=${OPTARG};;    # Benchmark name, e.g. perlbench
        o) OUTPUT_DIR=${OPTARG};;   # Directory to place run output. Make sure this exists!
        f) fastforwardinsts=${OPTARG};;
        w) warmupinsts=${OPTARG};;
        m) maximuminsts=${OPTARG};;
        e) execMode=${OPTARG};;
        branchoutcomefile) branchOutcomeFile=${OPTARG};;
        -)
            case "${OPTARG}" in
                extractBranchOutcomes) extractBranchOutcomes=true;;
                extractLoadHints) extractLoadHints=true;;
                extractCommittedInsts) extractCommittedInsts=true;;
                issueInProgramOrder) issueInProgramOrder=true;;
                utilizeBranchHints) utilizeBranchHints=true;;
                *)
                    echo "Invalid option: --${OPTARG}"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Invalid option: -${flag}"
            exit 1
            ;;
    esac
done

ISA=X86  # Modify ISA if required
ISA_lower=$(echo "$ISA" | tr '[:upper:]' '[:lower:]')

GEM5_DIR=/home/ishaan/distrobox_ubuntu22/Yashas/gem5-EE748
SPEC_DIR=/home/ishaan/distrobox_ubuntu22/spec2017  # Adjust SPEC2017 path accordingly

######################### BENCHMARK CODENAMES ####################
declare -A BENCHMARK_CODES
BENCHMARK_CODES=(
    ["perlbench_r"]="500.perlbench_r"
    ["gcc_r"]="502.gcc_r"
    ["bwaves_r"]="503.bwaves_r"
    ["mcf_r"]="505.mcf_r"
    ["cactuBSSN_r"]="507.cactuBSSN_r"
    ["namd_r"]="508.namd_r"
    ["parest_r"]="510.parest_r"
    ["povray_r"]="511.povray_r"
    ["lbm_r"]="519.lbm_r"
    ["omnetpp_r"]="520.omnetpp_r"
    ["wrf_r"]="521.wrf_r"
    ["xalancbmk_r"]="523.xalancbmk_r"
    ["x264_r"]="525.x264_r"
    ["blender_r"]="526.blender_r"
    ["cam4_r"]="527.cam4_r"
    ["deepsjeng_r"]="531.deepsjeng_r"
    ["imagick_r"]="538.imagick_r"
    ["leela_r"]="541.leela_r"
    ["nab_r"]="544.nab_r"
    ["exchange2_r"]="548.exchange2_r"
    ["fotonik3d_r"]="549.fotonik3d_r"
    ["roms_r"]="554.roms_r"
    ["xz_r"]="557.xz_r"
    ["specrand_ir"]="999.specrand_ir"
)

# Get benchmark code
BENCHMARK_CODE=${BENCHMARK_CODES[$BENCHMARK]}
if [[ -z "$BENCHMARK_CODE" ]]; then
    echo "Invalid benchmark selection: $BENCHMARK"
    exit 1
fi

# Prepare output directory
TRACE_OUTPUT_DIR=$OUTPUT_DIR
OUTPUT_DIR+="/"$execMode
if [ -n "$utilizeBranchHints" ]; then
    OUTPUT_DIR+="withbranchutilization"
fi

mkdir -p $OUTPUT_DIR || echo "$OUTPUT_DIR already exists!"

# Run directory
RUN_DIR=$SPEC_DIR/benchspec/CPU/$BENCHMARK_CODE/build/build_base_mytest-m64.0000

# Logging
SCRIPT_OUT=$OUTPUT_DIR/runscript.log
echo "Command line: $0 $*" | tee $SCRIPT_OUT
echo "GEM5_DIR: $GEM5_DIR" | tee -a $SCRIPT_OUT
echo "SPEC_DIR: $SPEC_DIR" | tee -a $SCRIPT_OUT
echo "BENCHMARK: $BENCHMARK ($BENCHMARK_CODE)" | tee -a $SCRIPT_OUT
echo "OUTPUT_DIR: $OUTPUT_DIR" | tee -a $SCRIPT_OUT

# Change directory
echo "Changing to SPEC benchmark runtime directory: $RUN_DIR" | tee -a $SCRIPT_OUT
cd $RUN_DIR || exit 1

# Configure simulation parameters
memsize=4GB
cpuclock=3GHz
l1isize=32kB
l1iassoc=4
l1dsize=32kB
l1dassoc=4

if [[ "$execMode" == "OoO" ]]; then
    cputype=DerivO3CPU
elif [[ "$execMode" == "InO" ]]; then
    cputype=X86MinorCPU
else
    echo "Unsupported Execution Mode $execMode"
    exit 1
fi
echo $cputype | tee -a $SCRIPT_OUT
echo "Launching gem5"
# Launch gem5
# $GEM5_DIR/build/"$ISA"/gem5.opt --debug-flags=ScheduleTrace  --debug-file=${BENCHMARK}_schedule_trace --outdir=$OUTPUT_DIR $GEM5_DIR/configs/BTP/config_17.py --fast-forward $fastforwardinsts --warmup-insts $warmupinsts --maxinsts $maximuminsts --benchmark=$BENCHMARK --benchmark_stdout=$OUTPUT_DIR/$BENCHMARK.out --benchmark_stderr=$OUTPUT_DIR/$BENCHMARK.err | tee -a $SCRIPT_OUT
$GEM5_DIR/build/"$ISA"/gem5.opt --debug-flags=Context,Decode,O3CPU,ROB,ScheduleTrace --debug-file=${BENCHMARK}_schedule_trace --outdir=$OUTPUT_DIR $GEM5_DIR/configs/BTP/config_17.py --fast-forward $fastforwardinsts --warmup-insts $warmupinsts --maxinsts $maximuminsts --benchmark=$BENCHMARK --benchmark_stdout=$OUTPUT_DIR/$BENCHMARK.out --benchmark_stderr=$OUTPUT_DIR/$BENCHMARK.err | tee -a $SCRIPT_OUT
