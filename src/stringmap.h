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

#ifndef PYNINI_STRINGMAP_H_
#define PYNINI_STRINGMAP_H_

// This file contains functions for compiling FSTs from pairs of strings
// using a prefix tree.

#include <string>
using std::string;
#include <utility>
#include <vector>

#include <iostream>
#include <fst/fstlib.h>
#include "optimize.h"
#include "stringcompile.h"
#include "stringfile.h"
#include "prefix_tree.h"

namespace fst {
namespace internal {

// Adaptor for using a vector argument below.
class StringPairIterator {
 public:
  using V = std::vector<std::pair<string, string>>;
  using I = typename V::const_iterator;

  explicit StringPairIterator(const V &v) : it_(v.cbegin()), end_(v.cend()) {}

  void Next() { ++it_; }

  bool Done() const { return it_ == end_; }

  const string GetLeftString() { return it_->first; }

  const string GetRightString() { return it_->second; }

 private:
  I it_;
  I end_;
};

}  // namespace internal

// Compiles minimal deterministic FST representing the union of the
// cross-product of pairs of strings.
template <class Arc, class Data>
bool CompileStringMap(Data *data, StringTokenType itype, StringTokenType otype,
                      MutableFst<Arc> *fst, const SymbolTable *isyms = nullptr,
                      const SymbolTable *osyms = nullptr,
                      bool attach_symbols = true) {
  using Label = typename Arc::Label;
  using Weight = typename Arc::Weight;
  PrefixTree<Arc> ptree;
  std::unique_ptr<SymbolTable> new_isyms(
      internal::GetSymbolTable(itype, isyms));
  std::unique_ptr<SymbolTable> new_osyms(
      internal::GetSymbolTable(otype, osyms));
  // Converts the string pairs to vectors of arc labels.
  std::vector<Label> ilabels;
  std::vector<Label> olabels;
  for (; !data->Done(); data->Next()) {
    if (!StringToLabels<Label>(data->GetLeftString(), itype, &ilabels,
                               new_isyms.get())) {
      return false;
    }
    if (!StringToLabels<Label>(data->GetRightString(), otype, &olabels,
                               new_osyms.get())) {
      return false;
    }
    ptree.Add(ilabels.begin(), ilabels.end(), olabels.begin(), olabels.end(),
              Weight::One());
  }
  // Compiles the prefix tree into an FST.
  ptree.ToFst(fst);
  OptimizeStringCrossProducts(fst);
  // Optionally symbol tables.
  if (attach_symbols) {
    fst->SetInputSymbols(new_isyms.get());
    fst->SetOutputSymbols(new_osyms.get());
  }
  return true;
}

// Specialization for a vector of string pairs.
template <class Arc>
bool CompileStringMap(const std::vector<std::pair<string, string>> &data,
                      StringTokenType itype, StringTokenType otype,
                      MutableFst<Arc> *fst, const SymbolTable *isyms = nullptr,
                      const SymbolTable *osyms = nullptr,
                      bool attach_symbols = true) {
  internal::StringPairIterator spiter(data);
  return CompileStringMap(&spiter, itype, otype, fst, isyms, osyms,
                          attach_symbols);
}

// A helper for doing this from a TSV file.
template <class Arc>
bool CompileStringFile(const string &fname, StringTokenType itype,
                       StringTokenType otype, MutableFst<Arc> *fst,
                       const SymbolTable *isyms = nullptr,
                       const SymbolTable *osyms = nullptr,
                       bool attach_symbols = true) {
  std::ifstream istrm(fname);
    if (!istrm.good()) {    
    LOG(ERROR) << "Can't open file " << fname;
    return false;
  }
  internal::PairStringFile psf(istrm, fname);
  return CompileStringMap(&psf, itype, otype, fst, isyms, osyms,
                          attach_symbols);
}

}  // namespace fst

#endif  // PYNINI_STRINGMAP_H_

