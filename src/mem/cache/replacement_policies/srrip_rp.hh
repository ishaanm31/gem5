/**
 * @file
 * Declaration of a Re-Reference Interval Prediction replacement policy.
 *
 * Not-Recently Used (NRU) is an approximation of LRU that uses a single bit
 * to determine if an entry is going to be re-referenced in the near or distant
 * future.
 *
 * Re-Reference Interval Prediction (RRIP) is an extension of NRU that uses a
 * re-reference prediction value to determine if entries are going to be re-
 * used in the near future or not.
 *
 * The higher the value of the RRPV, the more distant the entry is from its
 * next access.
 *
 * Bimodal Re-Reference Interval Prediction (BRRIP) is an extension of RRIP
 * that has a probability of not inserting entries as the LRU. This probability
 * is controlled by the bimodal throtle parameter (btp).
 *
 * From the original paper, this implementation of RRIP is also called
 * Static RRIP (SRRIP), as it always inserts entries with the same RRPV.
 */

// Modified BRRIP RP files for implementation of SRRIP
// EE748
// Yashas M Salian (yashas.msalian@iitb.ac.in)

#ifndef __MEM_CACHE_REPLACEMENT_POLICIES_SRRIP_RP_HH__
#define __MEM_CACHE_REPLACEMENT_POLICIES_SRRIP_RP_HH__

#include "base/sat_counter.hh"
#include "mem/cache/replacement_policies/base.hh"

namespace gem5
{

struct SRRIPRPParams;

namespace replacement_policy
{

class SRRIP : public Base
{
  protected:
    /** SRRIP-specific implementation of replacement data. */
    struct SRRIPReplData : ReplacementData
    {
        /**
         * Re-Reference Interval Prediction Value.
         * Some values have specific names (according to the paper):
         * 0 -> near-immediate re-rereference interval
         * max_RRPV-1 -> long re-rereference interval
         * max_RRPV -> distant re-rereference interval
         */
        SatCounter8 rrpv;

        /** Whether the entry is valid. */
        bool valid;

        /**
         * Default constructor. Invalidate data.
         */
        SRRIPReplData(const int num_bits)
            : rrpv(num_bits), valid(false)
        {
        }
    };

    /**
     * Number of RRPV bits. An entry that saturates its RRPV has the longest
     * possible re-reference interval, that is, it is likely not to be used
     * in the near future, and is among the best eviction candidates.
     * A maximum RRPV of 1 implies in a NRU.
     */
    const unsigned numRRPVBits;

    /**
     * The hit priority (HP) policy replaces entries that do not receive cache
     * hits over any cache entry that receives a hit, while the frequency
     * priority (FP) policy replaces infrequently re-referenced entries.
     */
    const bool hitPriority;

  public:
    typedef SRRIPRPParams Params;
    SRRIP(const Params &p);
    ~SRRIP() = default;

    /**
     * Invalidate replacement data to set it as the next probable victim.
     * Set RRPV as the the most distant re-reference.
     *
     * @param replacement_data Replacement data to be invalidated.
     */
    void invalidate(const std::shared_ptr<ReplacementData>& replacement_data)
                                                                    override;

    /**
     * Touch an entry to update its replacement data.
     *
     * @param replacement_data Replacement data to be touched.
     */
    void touch(const std::shared_ptr<ReplacementData>& replacement_data) const
                                                                     override;

    /**
     * Reset replacement data. Used when an entry is inserted.
     * Set RRPV according to the insertion policy used.
     *
     * @param replacement_data Replacement data to be reset.
     */
    void reset(const std::shared_ptr<ReplacementData>& replacement_data) const
                                                                     override;

    /**
     * Find replacement victim using rrpv.
     *
     * @param cands Replacement candidates, selected by indexing policy.
     * @return Replacement entry to be replaced.
     */
    ReplaceableEntry* getVictim(const ReplacementCandidates& candidates) const
                                                                     override;

    /**
     * Instantiate a replacement data entry.
     *
     * @return A shared pointer to the new replacement data.
     */
    std::shared_ptr<ReplacementData> instantiateEntry() override;
};

} // namespace replacement_policy
} // namespace gem5

#endif // __MEM_CACHE_REPLACEMENT_POLICIES_SRRIP_RP_HH__
