/*
 * Copyright (c) 2012 ARM Limited
 * All rights reserved
 *
 * The license below extends only to copyright in the software and shall
 * not be construed as granting a license to any other intellectual
 * property including but not limited to intellectual property relating
 * to a hardware implementation of the functionality of the software
 * licensed hereunder.  You may use the software subject to the license
 * terms below provided that you ensure that this notice is replicated
 * unmodified and in its entirety in all distributions of the software,
 * modified or unmodified, in source code or in binary form.
 *
 * Copyright (c) 2004-2006 The Regents of The University of Michigan
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "cpu/o3/rob.hh"

#include <list>

#include "base/logging.hh"
#include "cpu/o3/dyn_inst.hh"
#include "cpu/o3/limits.hh"
#include "debug/Fetch.hh"
#include "debug/ROB.hh"
#include "params/BaseO3CPU.hh"

namespace gem5
{

namespace o3
{

ROB::ROB(CPU *_cpu, const BaseO3CPUParams &params)
    : robPolicy(params.smtROBPolicy),
      cpu(_cpu),
      numEntries(params.numROBEntries),
      squashWidth(params.squashWidth),
      numInstsInROB(0),
      numThreads(params.numThreads),
      issueInProgramOrder(params.issueInProgramOrder),
      utilizeBranchHints(params.utilizeBranchHints),
      stats(_cpu)
{
    //Figure out rob policy
    if (robPolicy == SMTQueuePolicy::Dynamic) {
        //Set Max Entries to Total ROB Capacity
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = numEntries;
        }

    } else if (robPolicy == SMTQueuePolicy::Partitioned) {
        DPRINTF(Fetch, "ROB sharing policy set to Partitioned\n");

        //@todo:make work if part_amt doesnt divide evenly.
        int part_amt = numEntries / numThreads;

        //Divide ROB up evenly
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = part_amt;
        }

    } else if (robPolicy == SMTQueuePolicy::Threshold) {
        DPRINTF(Fetch, "ROB sharing policy set to Threshold\n");

        int threshold =  params.smtROBThreshold;;

        //Divide up by threshold amount
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = threshold;
        }
    }

    for (ThreadID tid = numThreads; tid < MaxThreads; tid++) {
        maxEntries[tid] = 0;
    }

    resetState();
}

void
ROB::resetState()
{
    for (ThreadID tid = 0; tid  < MaxThreads; tid++) {
        threadEntries[tid] = 0;
        squashIt[tid] = instList[tid].end();
        if(issueInProgramOrder) {
            scheduleinstsquashIt[tid] = scheduleinstList[tid].end();
            doneScheduleInstListSquashing[tid] = true;
            // Below flag is set to true only when we have squashed head of scheduleinstList
            doneScheduleInstListHeadSquashing[tid] = false;
        }    
        squashedSeqNum[tid] = 0;
        doneSquashing[tid] = true;
    }
    numInstsInROB = 0;

    // Initialize the "universal" ROB head & tail point to invalid
    // pointers
    head = instList[0].end();
    tail = instList[0].end();
}

std::string
ROB::name() const
{
    return cpu->name() + ".rob";
}

void
ROB::setActiveThreads(std::list<ThreadID> *at_ptr)
{
    DPRINTF(ROB, "Setting active threads list pointer.\n");
    activeThreads = at_ptr;
}

void
ROB::drainSanityCheck() const
{
    for (ThreadID tid = 0; tid  < numThreads; tid++)
        assert(instList[tid].empty());
    assert(isEmpty());
}

void
ROB::takeOverFrom()
{
    resetState();
}

void
ROB::resetEntries()
{
    if (robPolicy != SMTQueuePolicy::Dynamic || numThreads > 1) {
        auto active_threads = activeThreads->size();

        std::list<ThreadID>::iterator threads = activeThreads->begin();
        std::list<ThreadID>::iterator end = activeThreads->end();

        while (threads != end) {
            ThreadID tid = *threads++;

            if (robPolicy == SMTQueuePolicy::Partitioned) {
                maxEntries[tid] = numEntries / active_threads;
            } else if (robPolicy == SMTQueuePolicy::Threshold &&
                       active_threads == 1) {
                maxEntries[tid] = numEntries;
            }
        }
    }
}

int
ROB::entryAmount(ThreadID num_threads)
{
    if (robPolicy == SMTQueuePolicy::Partitioned) {
        return numEntries / num_threads;
    } else {
        return 0;
    }
}

int
ROB::countInsts()
{
    int total = 0;

    for (ThreadID tid = 0; tid < numThreads; tid++)
        total += countInsts(tid);

    return total;
}

size_t
ROB::countInsts(ThreadID tid)
{
    return instList[tid].size();
}

void
ROB::insertInst(const DynInstPtr &inst)
{
    assert(inst);

    stats.writes++;

    DPRINTF(ROB, "Adding inst PC %s to the ROB.\n", inst->pcState());

    assert(numInstsInROB != numEntries);

    ThreadID tid = inst->threadNumber;

    instList[tid].push_back(inst);

    // Add instruction's PC and its sequence number in scheduleinstList at the same time as ROB
    if(issueInProgramOrder){
            ScheduleInstListEntry scheduleInstListEntry;
            scheduleInstListEntry.instPC = inst->pcState().instAddr();
            scheduleInstListEntry.seqNum = inst->seqNum;
            scheduleinstList[tid].push_back(scheduleInstListEntry);
    }

    //Set Up head iterator if this is the 1st instruction in the ROB
    if (numInstsInROB == 0) {
        head = instList[tid].begin();
        assert((*head) == inst);
    }

    //Must Decrement for iterator to actually be valid  since __.end()
    //actually points to 1 after the last inst
    tail = instList[tid].end();
    tail--;

    inst->setInROB();

    ++numInstsInROB;
    ++threadEntries[tid];

    assert((*tail) == inst);

    DPRINTF(ROB, "[tid:%i] Now has %d instructions.\n", tid,
            threadEntries[tid]);
}

void
ROB::retireHead(ThreadID tid)
{
    stats.writes++;

    assert(numInstsInROB > 0);

    // Get the head ROB instruction by copying it and remove it from the list
    InstIt head_it = instList[tid].begin();

    DynInstPtr head_inst = std::move(*head_it);
    instList[tid].erase(head_it);

    assert(head_inst->readyToCommit());

    DPRINTF(ROB, "[tid:%i] Retiring head instruction, "
            "instruction PC %s, [sn:%llu]\n", tid, head_inst->pcState(),
            head_inst->seqNum);

    --numInstsInROB;
    --threadEntries[tid];

    head_inst->clearInROB();
    head_inst->setCommitted();

    //Update "Global" Head of ROB
    updateHead();

    // @todo: A special case is needed if the instruction being
    // retired is the only instruction in the ROB; otherwise the tail
    // iterator will become invalidated.
    cpu->removeFrontInst(head_inst);
}

bool
ROB::isHeadReady(ThreadID tid)
{
    stats.reads++;
    if (threadEntries[tid] != 0) {
        return instList[tid].front()->readyToCommit();
    }

    return false;
}

bool
ROB::canCommit()
{
    //@todo: set ActiveThreads through ROB or CPU
    std::list<ThreadID>::iterator threads = activeThreads->begin();
    std::list<ThreadID>::iterator end = activeThreads->end();

    while (threads != end) {
        ThreadID tid = *threads++;

        if (isHeadReady(tid)) {
            return true;
        }
    }

    return false;
}

unsigned
ROB::numFreeEntries()
{
    return numEntries - numInstsInROB;
}

unsigned
ROB::numFreeEntries(ThreadID tid)
{
    return maxEntries[tid] - threadEntries[tid];
}

void
ROB::doSquash(ThreadID tid)
{
    stats.writes++;
    DPRINTF(ROB, "[tid:%i] Squashing instructions until [sn:%llu].\n",
            tid, squashedSeqNum[tid]);

    assert(squashIt[tid] != instList[tid].end());

    // Same logic as squashing in ROB. No extra case handling needed.
    if(issueInProgramOrder && !scheduleinstList[tid].empty()) {
        assert(scheduleinstsquashIt[tid] != scheduleinstList[tid].end());

        if((scheduleinstsquashIt[tid])->seqNum < squashedSeqNum[tid]) {
            DPRINTF(ROB, "[tid:%i] Done squashing instructions from schedule instruction list 1.\n",
                tid);

            scheduleinstsquashIt[tid] = scheduleinstList[tid].end();
            doneScheduleInstListSquashing[tid] = true;
        }
    }

    if ((*squashIt[tid])->seqNum < squashedSeqNum[tid]) {
        DPRINTF(ROB, "[tid:%i] Done squashing instructions.\n",
                tid);

        squashIt[tid] = instList[tid].end();

        doneSquashing[tid] = true;
        return;
    }

    bool robTailUpdate = false;

    unsigned int numInstsToSquash = squashWidth;

    // If the CPU is exiting, squash all of the instructions
    // it is told to, even if that exceeds the squashWidth.
    // Set the number to the number of entries (the max).
    if (cpu->isThreadExiting(tid))
    {
        numInstsToSquash = numEntries;
    }

    for (int numSquashed = 0;
         numSquashed < numInstsToSquash &&
         squashIt[tid] != instList[tid].end() &&
         (*squashIt[tid])->seqNum > squashedSeqNum[tid];
         ++numSquashed)
    {
        DPRINTF(ROB, "[tid:%i] Squashing instruction PC %s, seq num %i.\n",
                (*squashIt[tid])->threadNumber,
                (*squashIt[tid])->pcState(),
                (*squashIt[tid])->seqNum);

        // Mark the instruction as squashed, and ready to commit so that
        // it can drain out of the pipeline.
        (*squashIt[tid])->setSquashed();

        /** Ideally, once a branch outcome entry is read from BOQ, it can be popped from BOQ,
         * but in gem5, if an instruction has a fault, consecutive instructions are squashed and re-executed
         * once we return from trap, hence correct-path branch instructions will also be squashed.
         * Therefore, in below added code, we check if squashed instruction is branch, we decrement the head iterator of BOQ
         * that points to the branch outcome that must be utilized.
         * Branch Instruction that is squashed can be in ROB or in initial stages of pipeline.
         * Squashing of branch instructions in ROB is handled here, hence decrementHead function is called here.
         * @Todo : Deleting unused entries from BOQ.
         * 
        */
        if(utilizeBranchHints && (*squashIt[tid])->isControl()) {
            DPRINTF(ROB, "Decrementing BOQ Head Iterator. \n");
            boq->decrementHead(tid);
            BOQ::BOQEntry boq_entry = boq->readentryfromBOQ(tid);
            DPRINTF(ROB, "BOQ entry read PC: %#x Next PC: %#x Target PC: %#x Target Next PC: %#x Branch Direction : %d\n",
                    boq_entry.inst_pc_pc, boq_entry.inst_pc_npc, boq_entry.branch_target_pc, boq_entry.branch_target_npc, boq_entry.branch_direction);
        }

        if(issueInProgramOrder && !scheduleinstList[tid].empty()) {
            if (scheduleinstsquashIt[tid] == scheduleinstList[tid].begin()) {
                DPRINTF(ROB, "Reached head of schedule instruction list while "
                    "squashing.\n");

                // Squashing head of instruction list if it is in the mispredicted path of instructions
                // and its sequence number is greater than the sequence number of mispredicted branch instruction.
                if (scheduleinstsquashIt[tid]->seqNum > squashedSeqNum[tid] &&
                    !doneScheduleInstListHeadSquashing[tid]) {
                    DPRINTF(ROB, "Squashing head of schedule instruction list as well.\n");
                    // Set to true only once when we need to squash head of scheduleinstList
                    doneScheduleInstListHeadSquashing[tid] = true;
                    scheduleinstList[tid].erase(scheduleinstsquashIt[tid]);
                }

                scheduleinstsquashIt[tid] = scheduleinstList[tid].end();
                
                doneScheduleInstListSquashing[tid] = true;
            }
            // Entries are removed from scheduleinstList when they need to be squashed (wrong path)
            // and in retireHeadInstSchedule function
            if(!doneScheduleInstListSquashing[tid]) {
                DPRINTF(ROB, "Squashing instruction list PC %#x, seq num %i.\n",
                    (scheduleinstsquashIt[tid]->instPC),
                    (scheduleinstsquashIt[tid]->seqNum));
                scheduleinstList[tid].erase(scheduleinstsquashIt[tid]);
            }
        }

        (*squashIt[tid])->setCanCommit();


        if (squashIt[tid] == instList[tid].begin()) {
            DPRINTF(ROB, "Reached head of instruction list while "
                    "squashing.\n");

            squashIt[tid] = instList[tid].end();

            doneSquashing[tid] = true;

            return;
        }

        InstIt tail_thread = instList[tid].end();
        tail_thread--;

        if ((*squashIt[tid]) == (*tail_thread))
            robTailUpdate = true;

        squashIt[tid]--;
        if(issueInProgramOrder && !scheduleinstList[tid].empty()) scheduleinstsquashIt[tid]--;
    }

    // Same logic as squashing in ROB. No extra case handling needed.
    if(issueInProgramOrder && !scheduleinstList[tid].empty()) {
        if((scheduleinstsquashIt[tid])->seqNum <= squashedSeqNum[tid]) {
            DPRINTF(ROB, "[tid:%i] Done squashing instructions from schedule instruction list 2.\n",
                tid);

            scheduleinstsquashIt[tid] = scheduleinstList[tid].end();

            doneScheduleInstListSquashing[tid] = true;
        }
    }


    // Check if ROB is done squashing.
    if ((*squashIt[tid])->seqNum <= squashedSeqNum[tid]) {
        DPRINTF(ROB, "[tid:%i] Done squashing instructions.\n",
                tid);

        squashIt[tid] = instList[tid].end();

        doneSquashing[tid] = true;
    }

    if (robTailUpdate) {
        updateTail();
    }
}


void
ROB::updateHead()
{
    InstSeqNum lowest_num = 0;
    bool first_valid = true;

    // @todo: set ActiveThreads through ROB or CPU
    std::list<ThreadID>::iterator threads = activeThreads->begin();
    std::list<ThreadID>::iterator end = activeThreads->end();

    while (threads != end) {
        ThreadID tid = *threads++;

        if (instList[tid].empty())
            continue;

        if (first_valid) {
            head = instList[tid].begin();
            lowest_num = (*head)->seqNum;
            first_valid = false;
            continue;
        }

        InstIt head_thread = instList[tid].begin();

        DynInstPtr head_inst = (*head_thread);

        assert(head_inst != 0);

        if (head_inst->seqNum < lowest_num) {
            head = head_thread;
            lowest_num = head_inst->seqNum;
        }
    }

    if (first_valid) {
        head = instList[0].end();
    }

}

void
ROB::updateTail()
{
    tail = instList[0].end();
    bool first_valid = true;

    std::list<ThreadID>::iterator threads = activeThreads->begin();
    std::list<ThreadID>::iterator end = activeThreads->end();

    while (threads != end) {
        ThreadID tid = *threads++;

        if (instList[tid].empty()) {
            continue;
        }

        // If this is the first valid then assign w/out
        // comparison
        if (first_valid) {
            tail = instList[tid].end();
            tail--;
            first_valid = false;
            continue;
        }

        // Assign new tail if this thread's tail is younger
        // than our current "tail high"
        InstIt tail_thread = instList[tid].end();
        tail_thread--;

        if ((*tail_thread)->seqNum > (*tail)->seqNum) {
            tail = tail_thread;
        }
    }
}


void
ROB::squash(InstSeqNum squash_num, ThreadID tid)
{
    if (isEmpty(tid)) {
        DPRINTF(ROB, "Does not need to squash due to being empty "
                "[sn:%llu]\n",
                squash_num);

        return;
    }

    DPRINTF(ROB, "Starting to squash within the ROB.\n");

    robStatus[tid] = ROBSquashing;

    doneSquashing[tid] = false;

    if(issueInProgramOrder) {
        doneScheduleInstListSquashing[tid] = false;
        doneScheduleInstListHeadSquashing[tid] = false;
    }
        

    squashedSeqNum[tid] = squash_num;

    if (!instList[tid].empty()) {
        InstIt tail_thread = instList[tid].end();
        tail_thread--;

        squashIt[tid] = tail_thread;

        if(issueInProgramOrder) {
            if(scheduleinstList[tid].empty())
                DPRINTF(ROB, "Schedule Instruction List is empty. No need to squash.\n");
            else {
                ScheduleInstIt scheduleList_tail_thread = scheduleinstList[tid].end();
                scheduleList_tail_thread--;

                scheduleinstsquashIt[tid] = scheduleList_tail_thread;
            }
        }            

        doSquash(tid);
    }
}

const DynInstPtr&
ROB::readHeadInst(ThreadID tid)
{
    if (threadEntries[tid] != 0) {
        InstIt head_thread = instList[tid].begin();

        assert((*head_thread)->isInROB());

        return *head_thread;
    } else {
        return dummyInst;
    }
}

DynInstPtr
ROB::readTailInst(ThreadID tid)
{
    InstIt tail_thread = instList[tid].end();
    tail_thread--;

    return *tail_thread;
}

ROB::ROBStats::ROBStats(statistics::Group *parent)
  : statistics::Group(parent, "rob"),
    ADD_STAT(reads, statistics::units::Count::get(),
        "The number of ROB reads"),
    ADD_STAT(writes, statistics::units::Count::get(),
        "The number of ROB writes")
{
}

DynInstPtr
ROB::findInst(ThreadID tid, InstSeqNum squash_inst)
{
    for (InstIt it = instList[tid].begin(); it != instList[tid].end(); it++) {
        if ((*it)->seqNum == squash_inst) {
            return *it;
        }
    }
    return NULL;
}


/** Returns a pointer to the head instruction of a specific thread within
 *  schedule instruction list.
*/
const ROB::ScheduleInstListEntry&
ROB::readHeadInstSchedule(ThreadID tid)
{
    assert(!scheduleinstList[tid].empty());
    ScheduleInstIt head_inst = scheduleinstList[tid].begin();

    DPRINTF(ROB, "PC of Instruction that must be executed %#x, [sn:%llu].\n",
            (head_inst->instPC),
            (head_inst->seqNum));
    return *head_inst;
}

/** Retires the head instruction of a specific thread, removing it from the
 *  schedule instruction list.
 */
void
ROB::retireHeadInstSchedule(ThreadID tid)
{
    assert(!scheduleinstList[tid].empty());
    ScheduleInstListEntry head_inst = std::move(scheduleinstList[tid].front());
    DPRINTF(ROB, "[tid:%i] Retiring head instruction from schedule instruction list, "
            "instruction PC %#x, [sn:%llu]\n", tid, head_inst.instPC,
            head_inst.seqNum);
    scheduleinstList[tid].pop_front();
}

void
ROB::setBOQ(BOQ *boq_ptr)
{
    boq = boq_ptr;
}

} // namespace o3
} // namespace gem5
