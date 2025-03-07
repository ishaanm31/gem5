#include "cpu/o3/boq.hh"
#include "params/BaseO3CPU.hh"
#include "debug/BranchOutcomes.hh"
#include "debug/Fetch.hh"
#include "arch/generic/pcstate.hh"
#include "base/trace.hh"

namespace gem5
{

namespace o3
{

BOQ::BOQ(const BaseO3CPUParams &params) :
    branchOutcomeFile(params.branchOutcomeFile)
{
    DPRINTF(Fetch, "Successfully passed branch outcome file name %s\n", params.branchOutcomeFile);

    for (ThreadID tid = 0; tid  < MaxThreads; tid++) {
        numEntriesInBOQ[tid] = 0;
        /** Initialize the head to invalid pointer .*/
        head[tid] = BranchOutcomeQueue[tid].end();
    }
}

void
BOQ::insertBranchOutcome(ThreadID tid, const PCStateBase &pc, const PCStateBase &nextpc, MicroPC branch_target_upc,
        MicroPC branch_target_nupc, const bool branch_direction)
{
    DPRINTF(Fetch, "Adding entry PC: %#x Next PC: %#x.(%#x=>%#x) Branch Direction : %d to the BOQ. \n",
            pc.instAddr(), nextpc.instAddr(), branch_target_upc, branch_target_nupc, branch_direction);

    PCStateBase *pcs = pc.clone();
    auto &xpc = pcs->as<GenericISA::PCStateWithNext>();
    PCStateBase *nextpcs = nextpc.clone();
    auto &xnextpc = nextpcs->as<GenericISA::PCStateWithNext>();
    BOQ::BOQEntry boqentry;
    boqentry.inst_pc_pc = xpc.pc();
    boqentry.inst_pc_npc = xpc.npc();
    boqentry.branch_target_pc = xnextpc.pc();
    boqentry.branch_target_npc = xnextpc.npc();
    boqentry.branch_target_upc = branch_target_upc;
    boqentry.branch_target_nupc = branch_target_nupc;
    boqentry.branch_direction = branch_direction;
    BranchOutcomeQueue[tid].push_back(boqentry);

    //Set Up head iterator if this is the 1st entry in the BOQ
    if (numEntriesInBOQ[tid] == 0) {
        head[tid] = BranchOutcomeQueue[tid].begin();
    } else {
        head[tid]++;
    }
    
    assert(head[tid] != BranchOutcomeQueue[tid].end());

    numEntriesInBOQ[tid]++;

    DPRINTF(Fetch, "[tid:%i] BOQ now has %d instructions.\n", tid,
            numEntriesInBOQ[tid]);
}

const BOQ::BOQEntry &
BOQ::readentryfromBOQ(ThreadID tid)
{
    if(numEntriesInBOQ[tid] == 0) {
        DPRINTF(Fetch, "Fatal!!! BOQ is empty. Troubleshoot.\n");
    }
    return *head[tid];
}

void
BOQ::decrementHead(ThreadID tid)
{   
    DPRINTF(Fetch, "Decrement Head Function called.\n");
    head[tid]--;
    DPRINTF(Fetch, "[tid:%i] BOQ now has %d instructions.\n", tid,
            numEntriesInBOQ[tid]);
}

} // namespace o3
} // namespace gem5