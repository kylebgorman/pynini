#cython: language_level=3
# Copyright 2016-2020 Google LLC
#
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

# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.


from libcpp cimport bool
from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from cintegral_types cimport int32
from cintegral_types cimport int64

from cpywrapfst cimport ComposeOptions
from cpywrapfst cimport FstClass
from cpywrapfst cimport MutableFstClass
from cpywrapfst cimport QueueType
from cpywrapfst cimport SymbolTable
from cpywrapfst cimport TokenType
from cpywrapfst cimport WeightClass


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

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum PdtComposeFilter:
    PAREN_FILTER "fst::PdtComposeFilter::PAREN"
    EXPAND_FILTER "fst::PdtComposeFilter::EXPAND"
    EXPAND_PAREN_FILTER "fst::PdtComposeFilter::EXPAND_PAREN"

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum PdtParserType:
    PDT_LEFT_PARSER "fst::PdtParserType::LEFT"
    PDT_LEFT_SR_PARSER "fst::PdtParserType::LEFT_SR"


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


cdef extern from "<fst/util.h>" namespace "fst" nogil:

  bool ReadLabelPairs[L](const string &, vector[pair[L, L]] *, bool)

  bool WriteLabelPairs[L](const string &, const vector[pair[L, L]] &)


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


cdef extern from "crossscript.h" \
    namespace "fst::script" nogil:

  void Cross(const FstClass &, const FstClass &, MutableFstClass *)

cdef extern from "lenientlycomposescript.h" \
    namespace "fst::script" nogil:

  void LenientlyCompose(const FstClass &,
                        const FstClass &,
                        const FstClass &,
                        MutableFstClass *,
                        const ComposeOptions &)


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
                            TokenType,
                            TokenType,
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


cdef extern from "defaults.h" namespace "fst" nogil:

  TokenType GetDefaultTokenType()

  const SymbolTable *GetDefaultSymbols()

  void PushDefaults(TokenType token_type, const SymbolTable *);

  void PopDefaults()


cdef extern from "stringutil.h" \
    namespace "fst" nogil:

  string Escape(const string &)


cdef extern from "stringcompile.h" \
    namespace "fst" nogil:

  int64 kBosIndex
  int64 kEosIndex

  const SymbolTable &GeneratedSymbols()


cdef extern from "stringcompilescript.h" \
    namespace "fst::script" nogil:

  bool StringCompile(const string &,
                     MutableFstClass *,
                     TokenType,
                     const SymbolTable *,
                     const WeightClass &)


cdef extern from "stringmapscript.h" \
    namespace "fst::script" nogil:

  bool StringFileCompile(const string &,
                         MutableFstClass *,
                         TokenType,
                         TokenType,
                         const SymbolTable *,
                         const SymbolTable *)

  bool StringMapCompile(const vector[vector[string]] &,
                        MutableFstClass *,
                        TokenType,
                        TokenType,
                        const SymbolTable *,
                        const SymbolTable *)


cdef extern from "stringprintscript.h" \
    namespace "fst::script" nogil:

  bool StringPrint(const FstClass &,
                   string *,
                   TokenType,
                   const SymbolTable *)

