# Copyright (c) 2010, 2017, 2020 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2006-2007 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from m5.defines import buildEnv
from m5.objects.FuncUnit import *
from m5.params import *
from m5.SimObject import SimObject


class IntALU(FUDesc):
    opList = [OpDesc(opClass="IntAlu")]
    count = 6


class IntMultDiv(FUDesc):
    opList = [
        OpDesc(opClass="IntMult", opLat=3),
        OpDesc(opClass="IntDiv", opLat=20, pipelined=False),
    ]

    count = 2


class FP_ALU(FUDesc):
    opList = [
        OpDesc(opClass="FloatAdd", opLat=2),
        OpDesc(opClass="FloatCmp", opLat=2),
        OpDesc(opClass="FloatCvt", opLat=2),
    ]
    count = 4


class FP_MultDiv(FUDesc):
    opList = [
        OpDesc(opClass="FloatMult", opLat=4),
        OpDesc(opClass="FloatMultAcc", opLat=5),
        OpDesc(opClass="FloatMisc", opLat=3),
        OpDesc(opClass="FloatDiv", opLat=12, pipelined=False),
        OpDesc(opClass="FloatSqrt", opLat=24, pipelined=False),
    ]
    count = 2


class SIMD_Unit(FUDesc):
    opList = [
        OpDesc(opClass="SimdAdd"),
        OpDesc(opClass="SimdAddAcc"),
        OpDesc(opClass="SimdAlu"),
        OpDesc(opClass="SimdCmp"),
        OpDesc(opClass="SimdCvt"),
        OpDesc(opClass="SimdMisc"),
        OpDesc(opClass="SimdMult"),
        OpDesc(opClass="SimdMultAcc"),
        OpDesc(opClass="SimdMatMultAcc"),
        OpDesc(opClass="SimdShift"),
        OpDesc(opClass="SimdShiftAcc"),
        OpDesc(opClass="SimdDiv"),
        OpDesc(opClass="SimdSqrt"),
        OpDesc(opClass="SimdFloatAdd"),
        OpDesc(opClass="SimdFloatAlu"),
        OpDesc(opClass="SimdFloatCmp"),
        OpDesc(opClass="SimdFloatCvt"),
        OpDesc(opClass="SimdFloatDiv"),
        OpDesc(opClass="SimdFloatMisc"),
        OpDesc(opClass="SimdFloatMult"),
        OpDesc(opClass="SimdFloatMultAcc"),
        OpDesc(opClass="SimdFloatMatMultAcc"),
        OpDesc(opClass="SimdFloatSqrt"),
        OpDesc(opClass="SimdReduceAdd"),
        OpDesc(opClass="SimdReduceAlu"),
        OpDesc(opClass="SimdReduceCmp"),
        OpDesc(opClass="SimdFloatReduceAdd"),
        OpDesc(opClass="SimdFloatReduceCmp"),
        OpDesc(opClass="SimdExt"),
        OpDesc(opClass="SimdFloatExt"),
        OpDesc(opClass="SimdConfig"),
    ]
    count = 4


class PredALU(FUDesc):
    opList = [OpDesc(opClass="SimdPredAlu")]
    count = 1


class ReadPort(FUDesc):
    opList = [
        OpDesc(opClass="MemRead"),
        OpDesc(opClass="FloatMemRead"),
        OpDesc(opClass="SimdUnitStrideLoad"),
        OpDesc(opClass="SimdUnitStrideMaskLoad"),
        OpDesc(opClass="SimdStridedLoad"),
        OpDesc(opClass="SimdIndexedLoad"),
        OpDesc(opClass="SimdUnitStrideFaultOnlyFirstLoad"),
        OpDesc(opClass="SimdWholeRegisterLoad"),
    ]
    count = 0


class WritePort(FUDesc):
    opList = [
        OpDesc(opClass="MemWrite"),
        OpDesc(opClass="FloatMemWrite"),
        OpDesc(opClass="SimdUnitStrideStore"),
        OpDesc(opClass="SimdUnitStrideMaskStore"),
        OpDesc(opClass="SimdStridedStore"),
        OpDesc(opClass="SimdIndexedStore"),
        OpDesc(opClass="SimdWholeRegisterStore"),
    ]
    count = 0


class RdWrPort(FUDesc):
    opList = [
        OpDesc(opClass="MemRead"),
        OpDesc(opClass="MemWrite"),
        OpDesc(opClass="FloatMemRead"),
        OpDesc(opClass="FloatMemWrite"),
        OpDesc(opClass="SimdUnitStrideLoad"),
        OpDesc(opClass="SimdUnitStrideStore"),
        OpDesc(opClass="SimdUnitStrideMaskLoad"),
        OpDesc(opClass="SimdUnitStrideMaskStore"),
        OpDesc(opClass="SimdStridedLoad"),
        OpDesc(opClass="SimdStridedStore"),
        OpDesc(opClass="SimdIndexedLoad"),
        OpDesc(opClass="SimdIndexedStore"),
        OpDesc(opClass="SimdUnitStrideFaultOnlyFirstLoad"),
        OpDesc(opClass="SimdWholeRegisterLoad"),
        OpDesc(opClass="SimdWholeRegisterStore"),
    ]
    count = 4


class IprPort(FUDesc):
    opList = [OpDesc(opClass="IprAccess", opLat=3, pipelined=False)]
    count = 1

# Added custom FUs with count and latency same as MinorCPU model
class CustomIntALU(FUDesc):
    opList = [OpDesc(opClass="IntAlu", opLat=3)]
    count = 2


class CustomIntMult(FUDesc):
    opList = [OpDesc(opClass="IntMult", opLat=3)]
    count = 1


class CustomIntDiv(FUDesc):
    opList = [OpDesc(opClass="IntDiv", opLat=9, pipelined=False)]
    count = 1


class CustomFP_SIMD(FUDesc):
    opList = [
        OpDesc(opClass="FloatAdd", opLat=6),
        OpDesc(opClass="FloatCmp", opLat=6),
        OpDesc(opClass="FloatCvt", opLat=6),
        OpDesc(opClass="FloatMult", opLat=6),
        OpDesc(opClass="FloatMultAcc", opLat=6),
        OpDesc(opClass="FloatMisc", opLat=6),
        OpDesc(opClass="FloatDiv", opLat=6, pipelined=False),
        OpDesc(opClass="FloatSqrt", opLat=6, pipelined=False),
        OpDesc(opClass="SimdAdd", opLat=6),
        OpDesc(opClass="SimdAddAcc", opLat=6),
        OpDesc(opClass="SimdAlu", opLat=6),
        OpDesc(opClass="SimdCmp", opLat=6),
        OpDesc(opClass="SimdCvt", opLat=6),
        OpDesc(opClass="SimdMisc", opLat=6),
        OpDesc(opClass="SimdMult", opLat=6),
        OpDesc(opClass="SimdMultAcc", opLat=6),
        OpDesc(opClass="SimdMatMultAcc", opLat=6),
        OpDesc(opClass="SimdShift", opLat=6),
        OpDesc(opClass="SimdShiftAcc", opLat=6),
        OpDesc(opClass="SimdDiv", opLat=6),
        OpDesc(opClass="SimdSqrt", opLat=6),
        OpDesc(opClass="SimdFloatAdd", opLat=6),
        OpDesc(opClass="SimdFloatAlu", opLat=6),
        OpDesc(opClass="SimdFloatCmp", opLat=6),
        OpDesc(opClass="SimdFloatCvt", opLat=6),
        OpDesc(opClass="SimdFloatDiv", opLat=6),
        OpDesc(opClass="SimdFloatMisc", opLat=6),
        OpDesc(opClass="SimdFloatMult", opLat=6),
        OpDesc(opClass="SimdFloatMultAcc", opLat=6),
        OpDesc(opClass="SimdFloatMatMultAcc", opLat=6),
        OpDesc(opClass="SimdFloatSqrt", opLat=6),
        OpDesc(opClass="SimdReduceAdd", opLat=6),
        OpDesc(opClass="SimdReduceAlu", opLat=6),
        OpDesc(opClass="SimdReduceCmp", opLat=6),
        OpDesc(opClass="SimdFloatReduceAdd", opLat=6),
        OpDesc(opClass="SimdFloatReduceCmp", opLat=6),
        OpDesc(opClass="SimdAes", opLat=6),
        OpDesc(opClass="SimdAesMix", opLat=6),
        OpDesc(opClass="SimdSha1Hash", opLat=6),
        OpDesc(opClass="SimdSha1Hash2", opLat=6),
        OpDesc(opClass="SimdSha256Hash", opLat=6),
        OpDesc(opClass="SimdSha256Hash2", opLat=6),
        OpDesc(opClass="SimdShaSigma2", opLat=6),
        OpDesc(opClass="SimdShaSigma3", opLat=6),
        OpDesc(opClass="Matrix", opLat=6),
        OpDesc(opClass="MatrixMov", opLat=6),
        OpDesc(opClass="MatrixOP", opLat=6),
    ]
    count = 1


class CustomPredALU(FUDesc):
    opList = [OpDesc(opClass="SimdPredAlu", opLat=3)]
    count = 1


class CustomRdWrPort(FUDesc):
    opList = [
        OpDesc(opClass="MemRead", opLat=1),
        OpDesc(opClass="MemWrite", opLat=1),
        OpDesc(opClass="FloatMemRead", opLat=1),
        OpDesc(opClass="FloatMemWrite", opLat=1),
    ]
    count = 1


class CustomMiscALU(FUDesc):
    opList = [
        OpDesc(opClass="IprAccess", opLat=1, pipelined=False),
        OpDesc(opClass="InstPrefetch", opLat=1, pipelined=False),
    ]
    count = 1


class CustomVecALU(FUDesc):
    opList = [
        OpDesc(opClass="SimdUnitStrideLoad", opLat=1),
        OpDesc(opClass="SimdUnitStrideStore", opLat=1),
        OpDesc(opClass="SimdUnitStrideMaskLoad", opLat=1),
        OpDesc(opClass="SimdUnitStrideMaskStore", opLat=1),
        OpDesc(opClass="SimdStridedLoad", opLat=1),
        OpDesc(opClass="SimdStridedStore", opLat=1),
        OpDesc(opClass="SimdIndexedLoad", opLat=1),
        OpDesc(opClass="SimdIndexedStore", opLat=1),
        OpDesc(opClass="SimdUnitStrideFaultOnlyFirstLoad", opLat=1),
        OpDesc(opClass="SimdWholeRegisterLoad", opLat=1),
        OpDesc(opClass="SimdWholeRegisterStore", opLat=1),
        # OpDesc(opClass="SimdIntegerArith", opLat=1),
        # OpDesc(opClass="SimdFloatArith", opLat=1),
        # OpDesc(opClass="SimdFloatConvert", opLat=1),
        # OpDesc(opClass="SimdIntegerReduce", opLat=1),
        # OpDesc(opClass="SimdFloatReduce", opLat=1),
        OpDesc(opClass="SimdMisc", opLat=1),
        # OpDesc(opClass="SimdIntegerExtension", opLat=1),
        OpDesc(opClass="SimdConfig", opLat=1),
    ]
    count = 1
