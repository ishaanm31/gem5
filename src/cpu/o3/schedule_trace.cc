#include "cpu/o3/schedule_trace.hh"
#include "debug/ScheduleTrace.hh"

#include "cpu/checker/cpu.hh"
#include "cpu/o3/dyn_inst.hh"
#include "cpu/o3/fu_pool.hh"
#include "cpu/o3/limits.hh"
#include "cpu/timebuf.hh"
#include "debug/Activity.hh"
#include "debug/Drain.hh"
#include "debug/IEW.hh"
#include "debug/O3PipeView.hh"
#include "params/BaseO3CPU.hh"

namespace gem5
{
namespace o3
{

schedule_trace::schedule_trace_entry::schedule_trace_entry()
    : trace_hash(0), frequency(1), instruction_count(0) {}

void schedule_trace::schedule_trace_entry::add_instruction(const DynInstPtr &inst) {
    Sequence.push_back(inst->pcState().instAddr());
    if (instruction_count == 0) start_tick = curTick();
    instruction_count++;
    end_tick = curTick();
}

auto schedule_trace::schedule_trace_entry::get_trace_hash() {
    if (trace_hash == 0) {
        for (auto x : Sequence)
            trace_hash ^= x;
    }
    return trace_hash;
}

bool schedule_trace::schedule_trace_entry::merge_if_same(const schedule_trace_entry& other) {
    if (Sequence.size() != other.Sequence.size())
        return false;
    for (size_t i = 0; i < Sequence.size(); i++) {
        if (Sequence[i] != other.Sequence[i]) return false;
    }
    frequency++;
    return true;
}

int schedule_trace::schedule_trace_entry::get_frequency() {
    return frequency;
}

schedule_trace::schedule_trace() : current_trace_entry(nullptr) {}

schedule_trace::~schedule_trace() {
    for (auto& entry : table) {
        for (auto* trace_entry : entry.second) {
            delete trace_entry;
        }
    }
}

void schedule_trace::instruction_commit(const DynInstPtr &inst) {
    if (current_trace_entry == nullptr) {
        current_trace_entry = new schedule_trace_entry();
    }
    current_trace_entry->add_instruction(inst);

    if (!inst->isControl()) return;

    Addr current_address = inst->pcState().instAddr();
    Addr target_address = inst->branchTarget()->instAddr();

    if (target_address >= current_address)
        return;

    Addr current_trace_hash = current_trace_entry->get_trace_hash();

    if (table.find(current_trace_hash) != table.end()) {
        for (auto trace_entry : table[current_trace_hash]) {
            if (trace_entry->merge_if_same(*current_trace_entry)) {
                delete current_trace_entry;
                current_trace_entry = nullptr;
                return;
            }
        }
    }

    table[current_trace_hash].insert(current_trace_entry);
    current_trace_entry = nullptr;
}

void schedule_trace::print_stats() const{
    DPRINTF(ScheduleTrace,"Printing ScheduleTrace stats:\n");
    for (auto& entry : table) {
        DPRINTF(ScheduleTrace,"For trace hash: %llu\n", entry.first);
        for (auto* trace_entry : entry.second) {
            DPRINTF(ScheduleTrace,"Trace with frequency: %d, inst_count: %d, ticks: %d\n", trace_entry->get_frequency(), trace_entry->instruction_count, trace_entry->end_tick - trace_entry->start_tick);
        }
        DPRINTF(ScheduleTrace, "--------------\n");
    }
    DPRINTF(ScheduleTrace, "Done printing SchduleTrace stats\n");
}

} // namespace o3
} // namespace gem5