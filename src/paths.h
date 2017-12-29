// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Copyright 2017 and onwards Google, Inc.
//
// For general information on the Pynini grammar compilation library, see
// pynini.opengrm.org.

#ifndef PYNINI_PATHS_H_
#define PYNINI_PATHS_H_

// An iterative definition of all paths of an acyclic automaton.
//
// For a given path, one can ask for the input label sequence, output label
// sequence, and total weight.
//
// The PathIterator class is agnostic about labels and symbol tables; the
// StringPaths wrapper knows about this and also checks the input FST's
// properties (e.g., to make sure that it is acyclic).

#include <memory>
#include <sstream>
#include <string>
using std::string;
#include <vector>

#include <fst/fstlib.h>
#include "stringprint.h"

namespace fst {

constexpr int32 kInitialStateIsFinal = -2;
constexpr int32 kNewState = -1;

// An iterator to provide a succession of paths from an automaton. Calling
// Next() gets the next path. Done() returns true if all the paths have been
// visited. Accessible path values are ILabels()---the sequence of input
// labels, OLabels()---for output labels, and Weight().
//
// Note that PathIterator is symbol table and string-agnostic; consider using
// StringPaths if you need either.
template <class Arc>
class PathIterator {
 public:
  using Label = typename Arc::Label;
  using StateId = typename Arc::StateId;
  using ArcWeight = typename Arc::Weight;

  // When check_acyclic is set, checks acyclicity of the FST. An acyclic FST may
  // lead to infinite loops and thus check_acyclic should only be false when the
  // caller can ensure finite iteration (e.g., knowing the FST is acyclic;
  // limiting the number of iterated paths).
  explicit PathIterator(const Fst<Arc> &fst, bool check_acyclic = true);

  // Whether initialization was successful. Check this before accessing the
  // iterator if it was constructed with check=true.
  bool Error() const { return error_; }

  const std::vector<Label> &ILabels() const { return path_ilabels_; }

  const std::vector<Label> &OLabels() const { return path_olabels_; }

  ArcWeight Weight() const {
    auto weight = ArcWeight::One();
    for (const auto &path_weight : path_weights_) {
      weight = Times(weight, path_weight);
    }
    return weight;
  }

  void Reset();

  void Next();

  bool Done() const { return path_states_.empty(); }

 private:
  // If initialization failed.
  bool error_;
  // Copy of FST being iterated over.
  std::unique_ptr<const Fst<Arc>> fst_;
  // Vector of states visited on this path.
  std::vector<StateId> path_states_;
  // Vector of input labels.
  std::vector<Label> path_ilabels_;
  // Vector of output labels.
  std::vector<Label> path_olabels_;
  // Vector of weights.
  std::vector<ArcWeight> path_weights_;
  // Vector of offsets for each arc iterator for each state, so that we can
  // remember where we left off. Note that -2 (kInitialStateIsFinal) and -1
  // (kNewState) here have special meanings, on which see below.
  std::vector<int32> arc_iterator_offsets_;
  bool pop_labels_;

  PathIterator(const PathIterator &) = delete;
  PathIterator &operator=(const PathIterator &) = delete;
};

template <class Arc>
PathIterator<Arc>::PathIterator(const Fst<Arc> &fst, bool check_acyclic)
    : error_(false), fst_(fst.Copy()), pop_labels_(false) {
  if (check_acyclic && !fst.Properties(kAcyclic, true)) {
    error_ = true;
    FSTERROR() << "PathIterator: Cyclic FSTs have an infinite number of paths";
    return;
  }
  Reset();
}

template <class Arc>
void PathIterator<Arc>::Reset() {
  pop_labels_ = false;
  const auto start = fst_->Start();
  if (start == kNoStateId) return;
  // Seeds the search with the start state.
  path_states_.push_back(start);
  const auto weight = fst_->Final(start);
  path_weights_.push_back(weight);
  // If the initial state is also a final state, then Next() has immediate work
  // to do, so we indicate that with kInitialStateIsFinal. Otherwise we set it
  // to kNewState, which means "I haven't started the arc iterator at this state
  // yet".
  arc_iterator_offsets_.push_back(weight == ArcWeight::Zero() ?
                                  kNewState : kInitialStateIsFinal);
  Next();
}

template <class Arc>
void PathIterator<Arc>::Next() {
  if (Done()) return;
  if (arc_iterator_offsets_.back() == kInitialStateIsFinal) {
    arc_iterator_offsets_.pop_back();
    arc_iterator_offsets_.push_back(kNewState);
    return;
  }
  // At the current state (the back of path_states_) we increment the
  // arc_iterator offset (meaning that if it's -1, aka kNewState, then we set it
  // to 0 and therefore start reading).
  StateId nextstate;
  while (!Done()) {
    int32 offset = arc_iterator_offsets_.back() + 1;
    arc_iterator_offsets_.pop_back();
    arc_iterator_offsets_.push_back(offset);
    ArcIterator<Fst<Arc>> aiter(*fst_, path_states_.back());
    aiter.Seek(offset);
    // If the arc iterator is done, then we are done at this state, and we move
    // back.
    if (aiter.Done()) {
      path_states_.pop_back();
      if (pop_labels_) {
        path_ilabels_.pop_back();
        path_olabels_.pop_back();
      }
      pop_labels_ = true;
      path_weights_.pop_back();
      arc_iterator_offsets_.pop_back();
      // Otherwise we proceed moving to the current arc's next state, then break
      // out of this loop and attempt to move forward.
    } else {
      const auto &arc = aiter.Value();
      if (pop_labels_) {
        path_ilabels_.pop_back();
        path_olabels_.pop_back();
      }
      pop_labels_ = true;
      path_ilabels_.push_back(arc.ilabel);
      path_olabels_.push_back(arc.olabel);
      path_weights_.pop_back();
      path_weights_.push_back(arc.weight);
      nextstate = arc.nextstate;
      break;
    }
  }
  if (Done()) return;
  // Now we proceed forward until we hit a final state.
  while (nextstate != kNoStateId) {
    path_states_.push_back(nextstate);
    const auto weight = fst_->Final(nextstate);
    if (weight == ArcWeight::Zero()) {
      ArcIterator<Fst<Arc>> aiter(*fst_, nextstate);
      if (aiter.Done()) {
        // We reached a non-final state with no exiting arcs. Pop it. This
        // shouldn't happen unless someone passes an unconnected machine.
        path_states_.pop_back();
        return;
      } else {
        const auto &arc = aiter.Value();
        path_ilabels_.push_back(arc.ilabel);
        path_olabels_.push_back(arc.olabel);
        path_weights_.push_back(arc.weight);
        arc_iterator_offsets_.push_back(0);
        nextstate = arc.nextstate;
      }
    } else {
      // If we are at a final state, we act as if we have taken a transition to
      // a hallucinated superfinal state which is the "real" final state and
      // which is the sole destination for any arc leaving a final state. This
      // bit of pretend is necessary so that we don't actually rewind in the
      // case that there are valid suffixes of the path terminating here, as in
      // something like /foo(bar)?/. Path weights and arc iterator offsets will
      // be popped on the next iteration, but we will not pop labels as no arcs
      // in the input FST are being traversed here.
      pop_labels_ = false;
      path_weights_.push_back(weight);
      arc_iterator_offsets_.push_back(-1);
      return;
    }
  }
}

// StringPaths is a wrapper for PathIterator that handles symbol tables, and
// the conversion of the label sequences to strings.
template <class Arc>
class StringPaths {
 public:
  using Label = typename Arc::Label;
  using StateId = typename Arc::StateId;
  using ArcWeight = typename Arc::Weight;

  // When check_acyclic is set, checks acyclicity of FST. An acyclic FST may
  // lead to infinite loops and thus check_acyclic should only be false when the
  // caller can ensure finite iteration (e.g., knowing the FST is acyclic or
  // limiting the number of iterated paths).
  StringPaths(const Fst<Arc> &fst, StringTokenType itype, StringTokenType otype,
              const SymbolTable *isyms = nullptr,
              const SymbolTable *osyms = nullptr, bool rm_epsilon = true,
              bool check_acyclic = true);

  // Same as above, but applies the same string token type and symbol table
  // to both tapes.
  StringPaths(const Fst<Arc> &fst, StringTokenType type,
              const SymbolTable *syms = nullptr, bool rm_epsilon = true,
              bool check_acyclic = true)
      : StringPaths(fst, type, type, syms, syms, rm_epsilon, check_acyclic) {}

  bool Error() const { return error_ || iter_.Error(); }

  // These return the underlying label sequences.

  void ILabels(std::vector<Label> *labels) const;

  std::vector<Label> ILabels() const;

  void OLabels(std::vector<Label> *labels) const;

  std::vector<Label> OLabels() const;

  ArcWeight Weight() const { return iter_.Weight(); }

  void IString(string *str);

  string IString();

  void OString(string *str);

  string OString();

  void Reset() { iter_.Reset(); }

  void Next() { iter_.Next(); }

  bool Done() const { return iter_.Done(); }

 private:
  void Labels(bool output, std::vector<Label> *labels) const;

  void MaybeRemoveEpsilonLabels(std::vector<Label> *labels) const {
    if (rm_epsilon_) internal::RemoveEpsilonLabels(labels);
  }

  PathIterator<Arc> iter_;
  StringTokenType itype_;
  StringTokenType otype_;
  const SymbolTable *isyms_;
  const SymbolTable *osyms_;
  bool error_;
  bool rm_epsilon_;
};

// When check_acyclic is set, checks acyclicity of FST. An acyclic FST may
// lead to infinite loops and thus check_acyclic should only be false when the
// caller can ensure finite iteration (e.g., knowing the FST is acyclic or
// limiting the number of iterated paths).
template <class Arc>
StringPaths<Arc>::StringPaths(const Fst<Arc> &fst, StringTokenType itype,
                              StringTokenType otype,
                              const SymbolTable *isyms /* = nullptr */,
                              const SymbolTable *osyms /* = nullptr */,
                              bool rm_epsilon /* = true */,
                              bool check_acyclic /* = true */)
    : iter_(fst, check_acyclic),
      itype_(itype),
      otype_(otype),
      isyms_(isyms),
      osyms_(osyms),
      error_(false),
      rm_epsilon_(rm_epsilon) {
  // If the FST has its own symbol tables and symbol table use is requested,
  // we use those unless isyms or osyms is specified.
  if (itype == StringTokenType::SYMBOL) {
    if (!isyms_ && fst.InputSymbols()) {
      isyms_ = fst.InputSymbols();
    }
  }
  if (otype == StringTokenType::SYMBOL) {
    if (!osyms_ && fst.OutputSymbols()) {
      osyms_ = fst.OutputSymbols();
    }
  }
  error_ = iter_.Error();
}

template <class Arc>
void StringPaths<Arc>::ILabels(std::vector<typename Arc::Label> *labels) const {
  *labels = iter_.ILabels();
  MaybeRemoveEpsilonLabels(labels);
}

template <class Arc>
void StringPaths<Arc>::OLabels(std::vector<typename Arc::Label> *labels) const {
  *labels = iter_.OLabels();
  MaybeRemoveEpsilonLabels(labels);
}

template <class Arc>
void StringPaths<Arc>::IString(string *str) {
  std::vector<Label> labels;
  ILabels(&labels);
  if (!internal::LabelsToString(labels, itype_, str, isyms_)) error_ = true;
}

template <class Arc>
string StringPaths<Arc>::IString() {
  string result;
  IString(&result);
  return result;
}

template <class Arc>
string StringPaths<Arc>::OString() {
  string result;
  OString(&result);
  return result;
}

template <class Arc>
void StringPaths<Arc>::OString(string *str) {
  std::vector<Label> labels;
  OLabels(&labels);
  if (!internal::LabelsToString(labels, otype_, str, osyms_)) error_ = true;
}

}  // namespace fst

#endif  // PYNINI_PATHS_H_

