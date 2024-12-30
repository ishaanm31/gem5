#ifndef __CPU_O3_ST_HH__
#define __CPU_O3_ST_HH__

#include <iostream>
#include <map>
#include <set>
#include <vector>

#include "base/statistics.hh"
#include "cpu/o3/comm.hh"
#include "cpu/o3/dyn_inst_ptr.hh"
#include "cpu/o3/inst_queue.hh"
#include "cpu/o3/limits.hh"
#include "cpu/o3/lsq.hh"
#include "cpu/o3/scoreboard.hh"
#include "cpu/timebuf.hh"
#include "debug/IEW.hh"
#include "sim/probe/probe.hh"

namespace gem5
{
namespace o3
{

class schedule_trace
{
private:
    class schedule_trace_entry
    {
    private:
        Addr trace_hash;
        std::vector<Addr> Sequence;
        int frequency;
    public:
        int instruction_count;
        Tick start_tick;
        Tick end_tick;
        schedule_trace_entry();
        void add_instruction(const DynInstPtr &inst);
        auto get_trace_hash();
        bool merge_if_same(const schedule_trace_entry& other);
        int get_frequency();
    };

    std::map<Addr, std::set<schedule_trace_entry*>> table;
    schedule_trace_entry *current_trace_entry;

public:
    schedule_trace();
    ~schedule_trace();
    void instruction_commit(const DynInstPtr &inst);
    void print_stats () const;
};

} // namespace o3
} // namespace gem5

#endif // __CPU_O3_ST_HH__