# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2017 and onwards Google, Inc.
#
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.


from libcpp cimport bool
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from libcpp.string cimport string

from basictypes cimport int32
from basictypes cimport int64

from fst cimport ComposeOptions
from fst cimport FstClass
from fst cimport MutableFstClass
from fst cimport SymbolTable
from fst cimport WeightClass


cdef extern from "crossproductscript.h" \
    namespace "fst::script" nogil:

  void CrossProduct(const FstClass &, const FstClass &, MutableFstClass *,
                    const WeightClass &)


cdef extern from "optimizescript.h" \
    namespace "fst::script" nogil:

  void Optimize(MutableFstClass *, bool)

  void OptimizeAcceptor(MutableFstClass *, bool)

  void OptimizeTransducer(MutableFstClass *, bool)

  void OptimizeStringCrossProducts(MutableFstClass *, bool)

  void OptimizeDifferenceRhs(MutableFstClass *, bool)


cdef extern from "<fst/string.h>" \
    namespace "fst" nogil:

  enum StringTokenType:
    SYMBOL
    BYTE
    UTF8

  SymbolTable *GetByteSymbolTable()


cdef extern from "pathsscript.h" \
    namespace "fst::script" nogil:

  cdef cppclass StringPathsClass:

    StringPathsClass(const FstClass &, StringTokenType, StringTokenType,
                     const SymbolTable *, const SymbolTable *, bool)

    bool Error()

    string IString()

    string OString()

    WeightClass Weight()

    vector[int64] ILabels()

    vector[int64] OLabels()

    void Reset()

    void Next()

    bool Done()


cdef extern from "lenientlycomposescript.h" \
    namespace "fst::script" nogil:

  void LenientlyCompose(const FstClass &, const FstClass &,
                        const FstClass &, MutableFstClass *,
                        const ComposeOptions &)


cdef extern from "repeatscript.h" \
    namespace "fst::script" nogil:

  void Repeat(MutableFstClass *, int32, int32)


cdef extern from "stringcompilescript.h" \
    namespace "fst::script" nogil:

  bool CompileString(const string &, const WeightClass &,
                     StringTokenType, MutableFstClass *,
                     const SymbolTable *, bool)


cdef extern from "stringmapscript.h" \
    namespace "fst::script" nogil:

  bool StringFile(const string &, StringTokenType, StringTokenType,
                  MutableFstClass *, const SymbolTable *, const SymbolTable *,
                  bool, bool)

  bool StringMap(const vector[vector[string]] &,
                 StringTokenType, StringTokenType, MutableFstClass *,
                 const SymbolTable *, const SymbolTable *,
                 bool, bool)


cdef extern from "stringprintscript.h" \
    namespace "fst::script" nogil:

  bool PrintString(const FstClass &, StringTokenType, string *,
                   const SymbolTable *, bool)


cdef extern from "stringtokentype.h" \
    namespace "fst::script" nogil:

  bool GetStringTokenType(const string &, StringTokenType *)


cdef extern from "merge.h" namespace "fst":

  enum MergeSymbolsType:
    MERGE_INPUT_SYMBOLS
    MERGE_OUTPUT_SYMBOLS
    MERGE_INPUT_AND_OUTPUT_SYMBOLS
    MERGE_LEFT_OUTPUT_AND_RIGHT_INPUT_SYMBOLS


cdef extern from "mergescript.h" \
    namespace "fst::script" nogil:

  void MergeSymbols(MutableFstClass *, MutableFstClass *, MergeSymbolsType)

