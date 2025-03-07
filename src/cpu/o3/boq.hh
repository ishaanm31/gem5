#ifndef __CPU_O3_BOQ_HH__
#define __CPU_O3_BOQ_HH__

#include "base/types.hh"
#include "arch/generic/pcstate.hh"
#include "base/compiler.hh"
#include "base/trace.hh"
#include "cpu/o3/limits.hh"
#include "params/BaseO3CPU.hh"

namespace gem5
{

struct BaseO3CPUParams;

namespace o3
{

class BOQ
{   
    public:
        /** BOQ constructor.
         *  @param p The cpu params including branch outcome file name parameter.
         */
        BOQ(const BaseO3CPUParams &p);

        /** Branch Outcome Text File. */
        std::ifstream branchOutcomeFile;

        /** Single entry in Branch Outcome Queue. */
        struct BOQEntry {
            Addr inst_pc_pc;
            Addr inst_pc_npc;
            Addr branch_target_pc;
            Addr branch_target_npc;
            MicroPC branch_target_upc;
            MicroPC branch_target_nupc;
            bool branch_direction;
        };

        /** Branch Outcome List of Instructions .*/
        std::list<BOQEntry> BranchOutcomeQueue[MaxThreads];

        /** Number of entries in the BOQ. */
        int numEntriesInBOQ[MaxThreads];

        typedef typename std::list<BOQEntry>::iterator BOQIt;

        /** Iterator that points to an entry in BOQ that must be utilized. */
        BOQIt head[MaxThreads];

    public:
        /** Function to insert a branch outcome into the BOQ. */
        void insertBranchOutcome(ThreadID tid, const PCStateBase &pc, const PCStateBase &nextpc, MicroPC branch_target_upc,
        MicroPC branch_target_nupc, const bool branch_direction);

        /** Returns a pointer to an entry of a specific thread within
        *  the BOQ that must be utilized.
        */
        const BOQEntry &readentryfromBOQ(ThreadID tid);

        /** Decrements the head iterator if any branch instruction is squashed .*/
        void decrementHead(ThreadID tid);
};

} // namespace o3
} // namespace gem5

#endif //__CPU_O3_BOQ_HH__