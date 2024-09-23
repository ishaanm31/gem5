// Implementation of SRRIP replacement policy for EE748, Assignment 1
// Yashas M Salian (yashas.msalian@iitb.ac.in)
// Based on in-built implementation of BRRIP

#include "mem/cache/replacement_policies/srrip_rp.hh"

#include <cassert>
#include <memory>

#include "base/logging.hh" // For fatal_if
#include "base/random.hh"
#include "params/SRRIPRP.hh"

namespace gem5
{

namespace replacement_policy
{

SRRIP::SRRIP(const Params &p)
  : Base(p), numRRPVBits(p.num_bits), hitPriority(p.hit_priority)
{
    fatal_if(numRRPVBits <= 0, "There should be at least one bit per RRPV.\n");
}

void
SRRIP::invalidate(const std::shared_ptr<ReplacementData>& replacement_data)
{
    std::shared_ptr<SRRIPReplData> casted_replacement_data =
        std::static_pointer_cast<SRRIPReplData>(replacement_data);

    // Invalidate entry
    casted_replacement_data->valid = false;
}

void
SRRIP::touch(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    std::shared_ptr<SRRIPReplData> casted_replacement_data =
        std::static_pointer_cast<SRRIPReplData>(replacement_data);

    // Update RRPV if not 0 yet
    // Every hit in HP mode makes the entry the last to be evicted, while
    // in FP mode a hit makes the entry less likely to be evicted
    if (hitPriority) {
        casted_replacement_data->rrpv.reset();
    } else {
        casted_replacement_data->rrpv--;
    }
}

void
SRRIP::reset(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    std::shared_ptr<SRRIPReplData> casted_replacement_data =
        std::static_pointer_cast<SRRIPReplData>(replacement_data);

    // Reset RRPV
    casted_replacement_data->rrpv.saturate();

    // Mark entry as ready to be used
    casted_replacement_data->valid = true;
}

ReplaceableEntry*
SRRIP::getVictim(const ReplacementCandidates& candidates) const
{
    // There must be at least one replacement candidate
    assert(candidates.size() > 0);

    // Use first candidate as dummy victim
    ReplaceableEntry* victim = candidates[0];

    // Store victim->rrpv in a variable to improve code readability
    int victim_RRPV = std::static_pointer_cast<SRRIPReplData>(
                        victim->replacementData)->rrpv;

    // Visit all candidates to find victim
    for (const auto& candidate : candidates) {
        std::shared_ptr<SRRIPReplData> candidate_repl_data =
            std::static_pointer_cast<SRRIPReplData>(
                candidate->replacementData);

        // Stop searching for victims if an invalid entry is found
        if (!candidate_repl_data->valid) {
            return candidate;
        }

        // Update victim entry if necessary
        int candidate_RRPV = candidate_repl_data->rrpv;
        if (candidate_RRPV > victim_RRPV) {
            victim = candidate;
            victim_RRPV = candidate_RRPV;
        }
    }

    // Get difference of victim's RRPV to the highest possible RRPV in
    // order to update the RRPV of all the other entries accordingly
    int diff = std::static_pointer_cast<SRRIPReplData>(
        victim->replacementData)->rrpv.saturate();

    // No need to update RRPV if there is no difference
    if (diff > 0){
        // Update RRPV of all candidates
        for (const auto& candidate : candidates) {
            std::static_pointer_cast<SRRIPReplData>(
                candidate->replacementData)->rrpv += diff;
        }
    }

    return victim;
}

std::shared_ptr<ReplacementData>
SRRIP::instantiateEntry()
{
    return std::shared_ptr<ReplacementData>(new SRRIPReplData(numRRPVBits));
}

} // namespace replacement_policy
} // namespace gem5
