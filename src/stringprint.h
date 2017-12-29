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

#ifndef PYNINI_STRINGPRINT_H_
#define PYNINI_STRINGPRINT_H_

#include <sstream>
#include <string>
using std::string;
#include <vector>

#include <fst/fst-decl.h>
#include <fst/icu.h>
#include <fst/string.h>

namespace fst {
namespace internal {

constexpr char kSymbolSeparator[] = " ";

// Collects output labels from a string FST. This is similar to the logic of
// the FST lib's string.h, but in function form.
template <class Arc>
bool FstToOutputLabels(const Fst<Arc> &fst,
                       std::vector<typename Arc::Label> *labels) {
  using Weight = typename Arc::Weight;
  labels->clear();
  auto s = fst.Start();
  if (s == kNoStateId) {
    LOG(ERROR) << "FstToOutputLabels: Invalid start state";
    return false;
  }
  while (fst.Final(s) == Weight::Zero()) {
    ArcIterator<Fst<Arc>> aiter(fst, s);
    if (aiter.Done()) {
      LOG(ERROR) << "FstToOutputLabels: String FST does not reach final state";
      return false;
    }
    const auto &arc = aiter.Value();
    labels->push_back(arc.olabel);
    s = arc.nextstate;
    if (s == kNoStateId) {
      LOG(ERROR) << "FstToOutputLabels: Transition to invalid state";
      return false;
    }
    aiter.Next();
    if (!aiter.Done()) {
      LOG(ERROR) << "FstToOutputLabels: State with multiple arcs";
      return false;
    }
  }
  return true;
}

// Prints a single symbol from a symbol table to a output stream.
template <class Label>
bool PrintSymbol(Label label, const SymbolTable &syms, std::ostream &ostrm) {
  const auto &symbol = syms.Find(label);
  if (symbol.empty()) {
    LOG(ERROR) << "PrintSymbol: Label " << label << "is not mapped to any "
               << "textual symbol in symbol table " << syms.Name();
    return false;
  }
  ostrm << symbol;
  return true;
}

// Writes an iterable of Labels into a string according to the user-specified
// StringTokenType. This is similar to the logic in the FST lib's string.h,
// but takes a lower-level input (a vector of labels) and avoids some redundant
// checks.
template <class Label>
bool LabelsToString(const std::vector<Label> &labels, StringTokenType ttype,
                    string *result, const SymbolTable *syms = nullptr) {
  result->clear();
  switch (ttype) {
    case BYTE: {
      result->reserve(labels.size());
      for (const auto &label : labels) result->push_back(label);
      return true;
    }
    case UTF8: {
      return LabelsToUTF8String(labels, result);
    }
    case SYMBOL: {
      std::stringstream sstrm;
      if (!syms) {
        LOG(ERROR) << "LabelsToString: Symbol table requested but not provided";
        return false;
      }
      auto it = labels.begin();
      if (it == labels.end()) return true;
      if (!PrintSymbol(*it, *syms, sstrm)) return false;
      for (++it; it != labels.end(); ++it) {
        sstrm << kSymbolSeparator;
        if (!PrintSymbol(*it, *syms, sstrm)) return false;
      }
      *result = sstrm.str();
      return true;
    }
  }
  return false;
}

// Removes epsilon labels (those which do not evaluate to true when cast to
// bool, so normally 0) from a vector of labels.
template <class Label>
void RemoveEpsilonLabels(std::vector<Label> *labels) {
  std::vector<Label> epsilon_free_labels;
  std::copy_if(labels->begin(), labels->end(),
               std::back_inserter(epsilon_free_labels),
               [](const Label i) { return i; });
  *labels = epsilon_free_labels;
}

}  // namespace internal

template <class Arc>
bool PrintString(const Fst<Arc> &fst, StringTokenType ttype, string *str,
                 const SymbolTable *syms = nullptr, bool rm_epsilon = true) {
  using Label = typename Arc::Label;
  // Collects labels.
  std::vector<Label> labels;
  if (!internal::FstToOutputLabels(fst, &labels)) return false;
  // Optionally removes epsilon labels.
  if (rm_epsilon) internal::RemoveEpsilonLabels(&labels);
  // Writes labels or symbols to string.
  if (!internal::LabelsToString(labels, ttype, str, syms)) return false;
  return true;
}

}  // namespace fst

#endif  // PYNINI_STRINGPRINT_H_

