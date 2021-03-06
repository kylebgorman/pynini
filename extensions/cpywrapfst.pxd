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

# See www.openfst.org for extensive documentation on this weighted
# finite-state transducer library.


from libcpp cimport bool
from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.utility cimport pair

from cios cimport *
from cintegral_types cimport *


cdef extern from "<fst/util.h>" nogil:

  bool FST_FLAGS_fst_error_fatal


cdef extern from "<fst/fstlib.h>" namespace "fst" nogil:

  # FST properties.
  const uint64 kExpanded
  const uint64 kMutable
  const uint64 kError
  const uint64 kAcceptor
  const uint64 kNotAcceptor
  const uint64 kIDeterministic
  const uint64 kNonIDeterministic
  const uint64 kODeterministic
  const uint64 kNonODeterministic
  const uint64 kEpsilons
  const uint64 kNoEpsilons
  const uint64 kIEpsilons
  const uint64 kNoIEpsilons
  const uint64 kOEpsilons
  const uint64 kNoOEpsilons
  const uint64 kILabelSorted
  const uint64 kNotILabelSorted
  const uint64 kOLabelSorted
  const uint64 kNotOLabelSorted
  const uint64 kWeighted
  const uint64 kUnweighted
  const uint64 kCyclic
  const uint64 kAcyclic
  const uint64 kInitialCyclic
  const uint64 kInitialAcyclic
  const uint64 kTopSorted
  const uint64 kNotTopSorted
  const uint64 kAccessible
  const uint64 kNotAccessible
  const uint64 kCoAccessible
  const uint64 kNotCoAccessible
  const uint64 kString
  const uint64 kNotString
  const uint64 kWeightedCycles
  const uint64 kUnweightedCycles
  const uint64 kNullProperties
  const uint64 kCopyProperties
  const uint64 kIntrinsicProperties
  const uint64 kExtrinsicProperties
  const uint64 kSetStartProperties
  const uint64 kSetFinalProperties
  const uint64 kAddStateProperties
  const uint64 kAddArcProperties
  const uint64 kSetArcProperties
  const uint64 kDeleteStatesProperties
  const uint64 kDeleteArcsProperties
  const uint64 kStateSortProperties
  const uint64 kArcSortProperties
  const uint64 kILabelInvariantProperties
  const uint64 kOLabelInvariantProperties
  const uint64 kWeightInvariantProperties
  const uint64 kAddSuperFinalProperties
  const uint64 kRmSuperFinalProperties
  const uint64 kBinaryProperties
  const uint64 kTrinaryProperties
  const uint64 kPosTrinaryProperties
  const uint64 kNegTrinaryProperties
  const uint64 kFstProperties

  # ArcIterator flags.
  const uint8 kArcILabelValue
  const uint8 kArcOLabelValue
  const uint8 kArcWeightValue
  const uint8 kArcNextStateValue
  const uint8 kArcNoCache
  const uint8 kArcValueFlags
  const uint8 kArcFlags

  # EncodeMapper flags.
  const uint8 kEncodeLabels
  const uint8 kEncodeWeights
  const uint8 kEncodeFlags

  # Default argument constants.
  const float kDelta
  const float kShortestDelta
  const int kNoLabel
  const int kNoStateId
  const int64 kNoSymbol

  enum ClosureType:
    CLOSURE_STAR
    CLOSURE_PLUS

  enum ComposeFilter:
    AUTO_FILTER
    NULL_FILTER
    SEQUENCE_FILTER
    ALT_SEQUENCE_FILTER
    MATCH_FILTER
    TRIVIAL_FILTER

  cdef cppclass ComposeOptions:

    ComposeOptions(bool, ComposeFilter)

  enum DeterminizeType:
    DETERMINIZE_FUNCTIONAL
    DETERMINIZE_NONFUNCTIONAL
    DETERMINIZE_DISAMBIGUATE

  enum EncodeType:
    DECODE
    ENCODE

  enum EpsNormalizeType:
    EPS_NORM_INPUT
    EPS_NORM_OUTPUT

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum ProjectType:
    PROJECT_INPUT "fst::ProjectType::INPUT"
    PROJECT_OUTPUT "fst::ProjectType::OUTPUT"

  enum QueueType:
    TRIVIAL_QUEUE
    FIFO_QUEUE
    LIFO_QUEUE
    SHORTEST_FIRST_QUEUE
    TOP_ORDER_QUEUE
    STATE_ORDER_QUEUE
    SCC_QUEUE
    AUTO_QUEUE
    OTHER_QUEUE

  # This is a templated struct at the C++ level, but Cython does not support
  # templated structs unless we pretend they are full-blown classes.
  cdef cppclass RandGenOptions[RandArcSelection]:

    RandGenOptions(const RandArcSelection &, int32, int32, bool, bool)

  enum ReplaceLabelType:
    REPLACE_LABEL_NEITHER
    REPLACE_LABEL_INPUT
    REPLACE_LABEL_OUTPUT
    REPLACE_LABEL_BOTH

  enum ReweightType:
    REWEIGHT_TO_INITIAL
    REWEIGHT_TO_FINAL

  cdef cppclass SymbolTableTextOptions:

    SymbolTableTextOptions(bool)

  # This is actually a nested class, but Cython doesn't need to know that.
  cdef cppclass SymbolTableIterator "fst::SymbolTable::iterator":

      SymbolTableIterator(const SymbolTableIterator &)

      cppclass value_type:

        int64 Label()
        string Symbol()

      # When wrapped in a unique_ptr siter.Label() and siter.Symbol() are
      # ambiguous to Cython because there's no way to make the -> explicit.
      # This hacks around that.
      const value_type &Pair "operator*"()

      SymbolTableIterator &operator++()

      bool operator==(const SymbolTableIterator &, const SymbolTableIterator &)

      bool operator!=(const SymbolTableIterator &, const SymbolTableIterator &)


  # Symbol tables.
  cdef cppclass SymbolTable:

    @staticmethod
    int64 kNoSymbol

    SymbolTable()

    SymbolTable(const string &)

    @staticmethod
    SymbolTable *Read(const string &)

    # Aliased for overload.
    @staticmethod
    SymbolTable *ReadStream "Read"(istream &, const string &)

    @staticmethod
    SymbolTable *ReadText(const string &, const SymbolTableTextOptions &)

    int64 AddSymbol(const string &, int64)

    int64 AddSymbol(const string &)

    SymbolTable *Copy()

    # Aliased for overload.
    string FindSymbol "Find"(int64)

    # Aliased for overload.
    int64 FindIndex "Find"(const string &)

    # Aliased for overload.
    bool MemberSymbol "Member"(const string &)

    # Aliased for overload.
    bool MemberIndex "Member"(int64)

    void AddTable(const SymbolTable &)

    int64 GetNthKey(ssize_t)

    const string &Name()

    void SetName(const string &)

    const string &CheckSum()

    const string &LabeledCheckSum()

    bool Write(ostream &)

    bool Write(const string &)

    bool WriteText(ostream &)

    bool WriteText(const string &)

    SymbolTableIterator begin()

    SymbolTableIterator end()

    int64 AvailableKey()

    size_t NumSymbols()

  SymbolTable *CompactSymbolTable(const SymbolTable &syms)

  SymbolTable *MergeSymbolTable(const SymbolTable &, const SymbolTable &,
                                bool *)

  SymbolTable *FstReadSymbols(const string &, bool)

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603.
  ctypedef enum TokenType:
    SYMBOL "fst::TokenType::SYMBOL"
    BYTE "fst::TokenType::BYTE"
    UTF8 "fst::TokenType::UTF8"


cdef extern from "<fst/script/fstscript.h>" namespace "fst::script" nogil:

  cdef cppclass WeightClass:

    WeightClass()

    WeightClass(const WeightClass &)

    WeightClass(const string &, const string &)

    const string &Type()

    string ToString()

    bool Member()

    @staticmethod
    const WeightClass &Zero(const string &)

    @staticmethod
    const WeightClass &One(const string &)

    @staticmethod
    const WeightClass &NoWeight(const string &)

  # Alias.
  cdef bool Eq "operator=="(const WeightClass &, const WeightClass &)

  # Alias.
  cdef bool Ne "operator!="(const WeightClass &, const WeightClass &)

  cdef WeightClass Plus(const WeightClass &, const WeightClass &)

  cdef WeightClass Times(const WeightClass &, const WeightClass &)

  cdef WeightClass Divide(const WeightClass &, const WeightClass &)

  cdef WeightClass Power(const WeightClass &, size_t)

  cdef cppclass ArcClass:

    ArcClass(const ArcClass &)

    ArcClass(int64, int64, const WeightClass &, int64)

    int64 ilabel
    int64 olabel
    WeightClass weight
    int64 nextstate

  cdef cppclass FstClass:

    FstClass(const FstClass &)

    @staticmethod
    FstClass *Read(const string &)

    # Aliased for overload.
    @staticmethod
    FstClass *ReadStream "Read"(istream &, const string &)

    int64 Start()

    WeightClass Final(int64)

    size_t NumArcs(int64)

    size_t NumInputEpsilons(int64)

    size_t NumOutputEpsilons(int64)

    const string &ArcType()

    const string &FstType()

    const SymbolTable *InputSymbols()

    const SymbolTable *OutputSymbols()

    const string &WeightType()

    bool Write(const string &)

    bool Write(ostream &, const string &)

    uint64 Properties(uint64, bool)

    bool ValidStateId(int64)

  cdef cppclass MutableFstClass(FstClass):

    bool AddArc(int64, const ArcClass &)

    int64 AddState()

    void AddStates(size_t)

    bool DeleteArcs(int64, size_t)

    bool DeleteArcs(int64)

    bool DeleteStates(const vector[int64] &)

    void DeleteStates()

    SymbolTable *MutableInputSymbols()

    SymbolTable *MutableOutputSymbols()

    int64 NumStates()

    bool ReserveArcs(int64, size_t)

    void ReserveStates(int64)

    bool SetStart(int64)

    bool SetFinal(int64, const WeightClass &)

    void SetInputSymbols(const SymbolTable *)

    void SetOutputSymbols(const SymbolTable *)

    void SetProperties(uint64, uint64)

  cdef cppclass VectorFstClass(MutableFstClass):

   VectorFstClass(const FstClass &)

   VectorFstClass(const string &)

  cdef cppclass EncodeMapperClass:

    EncodeMapperClass(const string &, uint32, EncodeType)

    # Aliased to __call__ as Cython doesn't have good support for operator().
    ArcClass __call__ "operator()"(const ArcClass &)

    const string &ArcType()

    const string &WeightType()

    uint32 Flags()

    uint64 Properties(uint64)

    @staticmethod
    EncodeMapperClass *Read(const string &)

    # Aliased for overload.
    @staticmethod
    EncodeMapperClass *ReadStream "Read"(istream &, const string &)

    bool Write(const string &)

    # Aliased for overload.
    bool WriteStream "Write"(ostream &, const string &)

    const SymbolTable *InputSymbols()

    const SymbolTable *OutputSymbols()

    void SetInputSymbols(const SymbolTable *)

    void SetOutputSymbols(const SymbolTable *)

  cdef cppclass ArcIteratorClass:

    ArcIteratorClass(const FstClass &, int64)

    bool Done()

    ArcClass Value()

    void Next()

    void Reset()

    void Seek(size_t)

    size_t Position()

    uint8 Flags()

    void SetFlags(uint8, uint8)

  cdef cppclass MutableArcIteratorClass:

    MutableArcIteratorClass(MutableFstClass *, int64)

    bool Done()

    ArcClass Value()

    void Next()

    void Reset()

    void Seek(size_t)

    void SetValue(const ArcClass &)

    size_t Position()

    uint8 Flags()

    void SetFlags(uint8, uint8)

  cdef cppclass StateIteratorClass:

    StateIteratorClass(const FstClass &)

    bool Done()

    int64 Value()

    void Next()

    void Reset()


ctypedef pair[int64, const FstClass *] LabelFstClassPair

ctypedef pair[int64, int64] LabelPair


cdef extern from "<fst/script/fstscript.h>" namespace "fst::script" nogil:

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum ArcFilterType:
    ANY_ARC_FILTER "fst::script::ArcFilterType::ANY"
    EPSILON_ARC_FILTER "fst::script::ArcFilterType::EPSILON"
    INPUT_EPSILON_ARC_FILTER "fst::script::ArcFilterType::INPUT_EPSILON"
    OUTPUT_EPSILON_ARC_FILTER "fst::script::ArcFilterType::OUTPUT_EPSILON"

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum ArcSortType:
    ILABEL_SORT "fst::script::ArcSortType::ILABEL"
    OLABEL_SORT "fst::script::ArcSortType::OLABEL"

  cdef void ArcSort(MutableFstClass *, ArcSortType)

  cdef ClosureType GetClosureType(bool)

  cdef void Closure(MutableFstClass *, ClosureType)

  cdef unique_ptr[FstClass] CompileFstInternal(istream &,
                                               const string &,
                                               const string &,
                                               const string &,
                                               const SymbolTable *,
                                               const SymbolTable *,
                                               const SymbolTable*,
                                               bool,
                                               bool,
                                               bool,
                                               bool,
                                               bool)

  cdef void Compose(FstClass &, FstClass &, MutableFstClass *,
                    const ComposeOptions &)

  cdef void Concat(MutableFstClass *, const FstClass &)

  cdef void Connect(MutableFstClass *)

  cdef unique_ptr[FstClass] Convert(const FstClass &, const string &)

  cdef void Decode(MutableFstClass *, const EncodeMapperClass &)

  cdef cppclass DeterminizeOptions:

    DeterminizeOptions(float,
                       const WeightClass &,
                       int64,
                       int64,
                       DeterminizeType,
                       bool)

  cdef void Determinize(const FstClass &,
                        MutableFstClass *,
                        const DeterminizeOptions &)

  cdef cppclass DisambiguateOptions:

    DisambiguateOptions(float, const WeightClass &, int64, int64)

  cdef void Disambiguate(const FstClass &,
                         MutableFstClass *,
                         const DisambiguateOptions &)

  cdef void Difference(const FstClass &,
                       const FstClass &,
                       MutableFstClass *,
                       const ComposeOptions &)

  cdef void Draw(const FstClass &fst,
                 const SymbolTable *,
                 const SymbolTable *,
                 const SymbolTable *,
                 bool,
                 const string &,
                 float,
                 float,
                 bool,
                 bool,
                 float,
                 float,
                 int,
                 int,
                 const string &,
                 bool,
                 ostream &,
                 const string &)

  cdef void Encode(MutableFstClass *, EncodeMapperClass *)

  cdef EpsNormalizeType GetEpsNormalizeType(bool)

  cdef void EpsNormalize(const FstClass &, MutableFstClass *, EpsNormalizeType)

  cdef bool Equal(const FstClass &, const FstClass &, float)

  cdef bool Equivalent(const FstClass &, const FstClass &, float)

  cdef void Intersect(const FstClass &,
                      const FstClass &,
                      MutableFstClass *,
                      const ComposeOptions &)

  cdef void Invert(MutableFstClass *fst)

  cdef bool Isomorphic(const FstClass &, const FstClass &, float)

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum MapType:
    ARC_SUM_MAPPER "fst::script::MapType::ARC_SUM"
    IDENTITY_MAPPER "fst::script::MapType::IDENTITY"
    INPUT_EPSILON_MAPPER "fst::script::MapType::INPUT_EPSILON"
    INVERT_MAPPER "fst::script::MapType::INVERT"
    OUTPUT_EPSILON_MAPPER "fst::script::MapType::OUTPUT_EPSILON"
    PLUS_MAPPER "fst::script::MapType::PLUS"
    QUANTIZE_MAPPER "fst::script::MapType::QUANTIZE"
    RMWEIGHT_MAPPER "fst::script::MapType::RMWEIGHT"
    SUPERFINAL_MAPPER "fst::script::MapType::SUPERFINAL"
    TIMES_MAPPER "fst::script::MapType::TIMES"
    TO_LOG_MAPPER "fst::script::MapType::TO_LOG"
    TO_LOG64_MAPPER "fst::script::MapType::TO_LOG64"
    TO_STD_MAPPER "fst::script::MapType::TO_STD"

  cdef unique_ptr[FstClass] Map(const FstClass &,
                                MapType,
                                float,
                                double,
                                const WeightClass &)

  cdef void Minimize(MutableFstClass *, MutableFstClass *, float, bool)

  cdef bool GetProjectType(const string &, ProjectType *)

  cdef void Project(MutableFstClass *, ProjectType)

  cdef void Print(const FstClass &,
                  ostream &,
                  const string &,
                  const SymbolTable *,
                  const SymbolTable *,
                  const SymbolTable *,
                  bool,
                  bool,
                  const string &)

  cdef void Prune(const FstClass &,
                  MutableFstClass *,
                  const WeightClass &,
                  int64, float)

  cdef void Prune(MutableFstClass *, const WeightClass &, int64, float)

  cdef void Push(const FstClass &,
                 MutableFstClass *,
                 uint8 flags,
                 ReweightType, float)

  cdef void Push(MutableFstClass *, ReweightType, float, bool)

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum RandArcSelection:
    UNIFORM_ARC_SELECTOR "fst::script::RandArcSelection::UNIFORM"
    LOG_PROB_ARC_SELECTOR "fst::script::RandArcSelection::LOG_PROB"
    FAST_LOG_PROB_ARC_SELECTOR "fst::script::RandArcSelection::FAST_LOG_PROB"

  cdef bool RandEquivalent(const FstClass &,
                           const FstClass &,
                           int32,
                           const RandGenOptions[RandArcSelection] &,
                           float,
                           uint64)

  cdef void RandGen(const FstClass &,
                    MutableFstClass *,
                    const RandGenOptions[RandArcSelection] &,
                    uint64)

  cdef void Relabel(MutableFstClass *,
                    const SymbolTable *,
                    const SymbolTable *,
                    const string &, bool,
                    const SymbolTable *,
                    const SymbolTable *,
                    const string &,
                    bool)

  cdef void Relabel(MutableFstClass *,
                    const vector[LabelPair] &,
                    const vector[LabelPair] &)

  cdef cppclass ReplaceOptions:

     ReplaceOptions(int64, ReplaceLabelType, ReplaceLabelType, int64)

  cdef void Replace(const vector[LabelFstClassPair] &,
                    MutableFstClass *,
                    const ReplaceOptions &)

  cdef void Reverse(const FstClass &, MutableFstClass *, bool)

  cdef void Reweight(MutableFstClass *,
                     const vector[WeightClass] &,
                     ReweightType)

  cdef cppclass RmEpsilonOptions:

    RmEpsilonOptions(QueueType, bool, const WeightClass &, int64, float)

  cdef void RmEpsilon(MutableFstClass *, const RmEpsilonOptions &)

  cdef cppclass ShortestDistanceOptions:

    ShortestDistanceOptions(QueueType, ArcFilterType, int64, float)

  cdef void ShortestDistance(const FstClass &,
                             vector[WeightClass] *,
                             const ShortestDistanceOptions &)

  cdef void ShortestDistance(const FstClass &,
                             vector[WeightClass] *, bool,
                             float)

  cdef cppclass ShortestPathOptions:

    ShortestPathOptions(QueueType,
                        int32,
                        bool,
                        float,
                        const WeightClass &,
                        int64)

  cdef void ShortestPath(const FstClass &,
                         MutableFstClass *,
                         const ShortestPathOptions &)

  cdef void Synchronize(const FstClass &, MutableFstClass *)

  cdef bool TopSort(MutableFstClass *)

  cdef void Union(MutableFstClass *, const vector[FstClass *] &)

  cdef bool Verify(const FstClass &)


cdef extern from "<fst/script/getters.h>" namespace "fst::script" nogil:

  cdef bool GetArcSortType(const string &, ArcSortType *)

  cdef bool GetComposeFilter(const string &, ComposeFilter *)

  cdef bool GetDeterminizeType(const string &, DeterminizeType *)

  cdef uint8 GetEncodeFlags(bool, bool)

  cdef bool GetMapType(const string &, MapType *)

  cdef uint8 GetPushFlags(bool, bool, bool, bool)

  cdef bool GetQueueType(const string &, QueueType *)

  cdef bool GetRandArcSelection(const string &, RandArcSelection *)

  cdef bool GetReplaceLabelType(string, bool, ReplaceLabelType *)

  cdef ReweightType GetReweightType(bool)

  cdef bool GetTokenType(const string &, TokenType *)


cdef extern from "<fst/extensions/far/far.h>" namespace "fst" nogil:

  # TODO(wolfsonkin): Don't do this hack if Cython gets proper enum class
  # support: https://github.com/cython/cython/issues/1603
  ctypedef enum FarType:
    FAR_DEFAULT "fst::FarType::DEFAULT"
    FAR_STTABLE "fst::FarType::STTABLE"
    FAR_STLIST "fst::FarType::STLIST"
    FAR_FST "fst::FarType::FST"
    FAR_SSTABLE "fst::FarType::SSTABLE"

cdef extern from "<fst/extensions/far/getters.h>" \
    namespace "fst" nogil:

  string GetFarTypeString(FarType)


cdef extern from "<fst/extensions/far/getters.h>" \
    namespace "fst::script" nogil:

  bool GetFarType(const string &, FarType *)


cdef extern from "<fst/extensions/far/far-class.h>" \
    namespace "fst::script" nogil:

  cdef cppclass FarReaderClass:

    const string &ArcType()

    bool Done()

    bool Error()

    bool Find(const string &)

    const FstClass *GetFstClass()

    const string &GetKey()

    void Next()

    void Reset()

    FarType Type()

    # For simplicity, we always use the multiple-file one.
    @staticmethod
    unique_ptr[FarReaderClass] Open(const vector[string] &)

  cdef cppclass FarWriterClass:

    bool Add(const string &, const FstClass &)

    bool Error()

    const string &ArcType()

    FarType Type()

    @staticmethod
    unique_ptr[FarWriterClass] Create(const string &, const string &, FarType)

