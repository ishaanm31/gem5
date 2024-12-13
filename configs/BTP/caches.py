# Custom configuration for caches
# Yashas M Salian (yashas.msalian@iitb.ac.in)
# Derived from Cache template in Standard Library

from m5.objects import *
from typing import Type
from gem5.utils.override import *

class L1DCache(Cache):
    """
    A simple L1 data cache with default values.

    If the cache has a mostly exclusive downstream cache, ``writeback_clean``
    should be set to ``True``.
    """

    def __init__(
        self,
        size: str = "32kB",
        assoc: int = 4,
        tag_latency: int = 1,
        data_latency: int = 1,
        response_latency: int = 1,
        mshrs: int = 32,
        tgts_per_mshr: int = 20,
        writeback_clean: bool = False,
    ):
        super().__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = tag_latency
        self.data_latency = data_latency
        self.response_latency = response_latency
        self.mshrs = mshrs
        self.tgts_per_mshr = tgts_per_mshr
        self.writeback_clean = writeback_clean

class L1ICache(Cache):
    """
    A simple L1 instruction cache with default values.

    If the cache does not have a downstream cache or the downstream cache
    is mostly inclusive as usual, ``writeback_clean`` should be set to ``False``.
    """

    def __init__(
        self,
        size: str = "32kB",
        assoc: int = 4,
        tag_latency: int = 1,
        data_latency: int = 1,
        response_latency: int = 1,
        mshrs: int = 32,
        tgts_per_mshr: int = 20,
        writeback_clean: bool = True,
    ):
        super().__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = tag_latency
        self.data_latency = data_latency
        self.response_latency = response_latency
        self.mshrs = mshrs
        self.tgts_per_mshr = tgts_per_mshr
        self.writeback_clean = writeback_clean

class L2Cache(Cache):
    """
    A simple L2 Cache with default values.
    """

    def __init__(
        self,
        size: str = "256kB",
        assoc: int = 8,
        tag_latency: int = 3,
        data_latency: int = 3,
        response_latency: int = 3,
        mshrs: int = 32,
        tgts_per_mshr: int = 12,
        writeback_clean: bool = False,
        clusivity: Clusivity = "mostly_incl",
        PrefetcherCls: Type[BasePrefetcher] = BOPPrefetcher,
    ):
        super().__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = tag_latency
        self.data_latency = data_latency
        self.response_latency = response_latency
        self.mshrs = mshrs
        self.tgts_per_mshr = tgts_per_mshr
        self.writeback_clean = writeback_clean
        self.clusivity = clusivity
        self.prefetcher = PrefetcherCls()
        self.replacement_policy = LRURP()