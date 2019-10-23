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
from libcpp.string cimport string
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from basictypes cimport int32
from basictypes cimport int64

from fst cimport ComposeOptions
from fst cimport FstClass
from fst cimport MutableFstClass
from fst cimport QueueType
from fst cimport SymbolTable
from fst cimport WeightClass


ctypedef pair[int64, const FstClass *] LabelFstClassPair


cdef extern from "<fst/extensions/mpdt/mpdtlib.h>" namespace "fst" nogil:


  cdef cppclass MPdtComposeOptions:

    MPdtComposeOptions(bool, PdtComposeFilter)


  cdef cppclass MPdtExpandOptions:

    MPdtExpandOptions(bool, bool)


cdef extern from "<fst/extensions/mpdt/mpdtscript.h>" \
    namespace "fst::script" nogil:

    void MPdtCompose(const FstClass &,
                     const FstClass &,
                     const vector[pair[int64, int64]] &,
                     const vector[int64] &,
                     MutableFstClass *,
                     const MPdtComposeOptions &,
                     bool)

    void MPdtExpand(const FstClass &,
                    const vector[pair[int64, int64]] &,
                    const vector[int64] &,
                    MutableFstClass *,
                    const MPdtExpandOptions &)

    void MPdtReverse(const FstClass &,
                      const vector[pair[int64, int64]] &,
                     vector[int64] *,
                     MutableFstClass *)


cdef extern from "<fst/extensions/mpdt/read_write_utils.h>" \
    namespace "fst" nogil:

  bool ReadLabelTriples[L](const string &,
                           vector[pair[L, L]] *,
                           vector[L] *,
                           bool)

  # TODO(kbg): The last argument is actually const but externally Cython 0.28
  # freaks out if it is so annotated. Re-annotate it const once this has been
  # fixed with the most recent Cython release.
  bool WriteLabelTriples[L](const string &,
                            const vector[pair[L, L]] &,
                            vector[L] &)


cdef extern from "<fst/extensions/pdt/pdtlib.h>" namespace "fst" nogil:

  cdef cppclass PdtComposeOptions:

    PdtComposeOptions(bool, PdtComposeFilter)

  enum PdtComposeFilter:
    PAREN_FILTER
    EXPAND_FILTER
    EXPAND_PAREN_FILTER

  enum PdtParserType:
    PDT_LEFT_PARSER
    PDT_LEFT_SR_PARSER


cdef extern from "<fst/extensions/pdt/getters.h>" \
    namespace "fst::script" nogil:

  bool GetPdtComposeFilter(const string &, PdtComposeFilter *)


cdef extern from "<fst/extensions/pdt/pdtscript.h>" \
    namespace "fst::script" nogil:

  void PdtCompose(const FstClass &,
                  const FstClass &,
                  const vector[pair[int64, int64]] &,
                  MutableFstClass *,
                  const PdtComposeOptions &,
                  bool)

  cdef cppclass PdtExpandOptions:

    PdtExpandOptions(bool, bool, const WeightClass &)

  void PdtExpand(const FstClass &,
                 const vector[pair[int64, int64]] &,
                 MutableFstClass *,
                 const PdtExpandOptions &)

  bool GetPdtParserType(const string &, PdtParserType *)

  void PdtReplace(const vector[LabelFstClassPair] &,
                  MutableFstClass *,
                  vector[pair[int64, int64]] *,
                  int64,
                  PdtParserType,
                  int64,
                  const string &,
                  const string &)

  void PdtReverse(const FstClass &,
                  const vector[pair[int64, int64]] &,
                  MutableFstClass *)

  cdef cppclass PdtShortestPathOptions:

    PdtShortestPathOptions(QueueType, bool, bool)

  void PdtShortestPath(const FstClass &,
                       const vector[pair[int64, int64]] &,
                       MutableFstClass *,
                       const PdtShortestPathOptions &)


cdef extern from "<fst/fstlib.h>" namespace "fst" nogil:

  bool ReadLabelPairs[L](const string &, vector[pair[L, L]] *, bool)

  bool WriteLabelPairs[L](const string &, const vector[pair[L, L]] &)

  enum StringTokenType:
    SYMBOL
    BYTE
    UTF8


cdef extern from "cdrewrite.h" \
    namespace "fst" nogil:

  enum CDRewriteDirection:
    LEFT_TO_RIGHT
    RIGHT_TO_LEFT
    SIMULTANEOUS

  enum CDRewriteMode:
    OBLIGATORY
    OPTIONAL


cdef extern from "cdrewritescript.h" \
    namespace "fst::script" nogil:

  void CDRewriteCompile(const FstClass &,
                        const FstClass &,
                        const FstClass &,
                        const FstClass &,
                        MutableFstClass *,
                        CDRewriteDirection,
                        CDRewriteMode,
                        int64,
                        int64)


cdef extern from "concatrangescript.h" \
    namespace "fst::script" nogil:

  void ConcatRange(MutableFstClass *, int32, int32)


cdef extern from "getters.h" \
    namespace "fst::script" nogil:

  bool GetCDRewriteDirection(const string &, CDRewriteDirection *)

  bool GetCDRewriteMode(const string &, CDRewriteMode *)

  bool GetStringTokenType(const string &, StringTokenType *)


cdef extern from "crossproductscript.h" \
    namespace "fst::script" nogil:

  void CrossProduct(const FstClass &,
                    const FstClass &,
                    MutableFstClass *,
                    const WeightClass &)


cdef extern from "lenientlycomposescript.h" \
    namespace "fst::script" nogil:

  void LenientlyCompose(const FstClass &,
                        const FstClass &,
                        const FstClass &,
                        MutableFstClass *,
                        const ComposeOptions &)


cdef extern from "mergesymbols.h" namespace "fst":

  enum MergeSymbolsType:
    MERGE_INPUT
    MERGE_OUTPUT
    MERGE_INPUT_OUTPUT
    MERGE_INSIDE
    MERGE_OUTSIDE


cdef extern from "mergesymbolsscript.h" \
    namespace "fst::script" nogil:

  void MergeSymbols(MutableFstClass *, MutableFstClass *, MergeSymbolsType)


cdef extern from "optimizescript.h" \
    namespace "fst::script" nogil:

  void Optimize(MutableFstClass *, bool)

  void OptimizeAcceptor(MutableFstClass *, bool)

  void OptimizeTransducer(MutableFstClass *, bool)

  void OptimizeStringCrossProducts(MutableFstClass *, bool)

  void OptimizeDifferenceRhs(MutableFstClass *, bool)


cdef extern from "pathsscript.h" \
    namespace "fst::script" nogil:

  cdef cppclass StringPathIteratorClass:

    StringPathIteratorClass(const FstClass &,
                            StringTokenType,
                            StringTokenType,
                            const SymbolTable *,
                            const SymbolTable *)

    bool Done()

    bool Error()

    vector[int64] ILabels()

    string IString()

    void Next()

    void Reset()

    vector[int64] OLabels()

    string OString()

    WeightClass Weight()


cdef extern from "stringcompilescript.h" \
    namespace "fst" nogil:

  SymbolTable *GetByteSymbolTable()


cdef extern from "stringcompilescript.h" \
    namespace "fst::script" nogil:

  bool CompileString(const string &,
                     MutableFstClass *,
                     StringTokenType,
                     const SymbolTable *,
                     const WeightClass &, bool)


cdef extern from "stringmapscript.h" \
    namespace "fst::script" nogil:

  bool StringFileCompile(const string &,
                         MutableFstClass *,
                         StringTokenType,
                         StringTokenType,
                         const SymbolTable *,
                         const SymbolTable *,
                         bool,
                         bool)

  bool StringMapCompile(const vector[vector[string]] &,
                        MutableFstClass *,
                        StringTokenType,
                        StringTokenType,
                        const SymbolTable *,
                        const SymbolTable *,
                        bool,
                        bool)


cdef extern from "stringprintscript.h" \
    namespace "fst::script" nogil:

  bool PrintString(const FstClass &,
                   string *,
                   StringTokenType,
                   const SymbolTable *)

