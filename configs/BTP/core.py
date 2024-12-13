# Custom configuration for CPU core
# Yashas M Salian (yashas.msalian@iitb.ac.in)

from m5.objects import *

class X86_O3_Custom(X86O3CPU):
    decodeWidth = 2
    fetchWidth = 2
    issueWidth = 2
    commitWidth = 2
    branchPred = TAGE_SC_L_64KB(ras = ReturnAddrStack(numEntries = 32))
