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

#ifndef PYNINI_PYNINI_REPLACE_H_
#define PYNINI_PYNINI_REPLACE_H_

// This file contains two main utility functions which extends FST replacement
// in the style of Thrax. Rather than passing pairs of integer labels and the
// corresponding FSTs, the user first passes a root FST followed by a list of
// (string label, FST) replacement pairs. There are both arc-templated and
// template-free variants of this function.
//
// As per library style, both arc-templated library functions are called
// PyniniReplace (and disambigated by their arguments), whereas the
// template-free scriptland variants are called PyniniReplace and
// PyniniPdtReplace, respectively.
//
// Note that the dummy root is assigned to kNoLabel.

#include <algorithm>
#include <memory>
#include <string>
using std::string;
#include <utility>
#include <vector>

#include <fst/extensions/pdt/pdtlib.h>
#include <fst/extensions/pdt/pdtscript.h>
#include <fst/fstlib.h>
#include <fst/script/arg-packs.h>
#include <fst/script/fstscript.h>
#include "pynini_common.h"

namespace fst {
namespace internal {

// This internal-only helper converts the root FST plus a vector of string/FST
// pairs to a vector of Label/FST pairs, stripping and merging symbol tables
// as it goes. It is used both for FST and PDT replacement.

template <class Arc>
bool PrepareReplacePairs(
    const Fst<Arc> &root,
    const std::vector<std::pair<string, const Fst<Arc> *>> &pairs,
    std::vector<std::pair<typename Arc::Label, const Fst<Arc> *>> *new_pairs) {
  using Label = typename Arc::Label;
  const auto size = pairs.size();
  new_pairs->resize(size + 1);
  // During replacement, all symbols are kept in "global" input and output
  // tables attached to the root while symbol tables attached to the
  // replacement FSTs are deleted. The replacement routines copy symbol tables
  // from the first FST in the RTN set (which here is alwyas the root) to the
  // output FST, so we attach these global tables to a (copy of) the root.
  std::unique_ptr<SymbolTable> isyms(root.InputSymbols()->Copy());
  std::unique_ptr<SymbolTable> osyms(root.OutputSymbols()->Copy());
  // The first time through, we put a dummy index index into the first slot of
  // each pair, as we don't have the complete symbol table yet.
  for (size_t i = 0; i < size; ++i) {
    auto *replace_fst = new VectorFst<Arc>(*pairs[i].second);
    isyms.reset(PrepareInputSymbols(isyms.get(), replace_fst));
    osyms.reset(PrepareOutputSymbols(osyms.get(), replace_fst));
    DeleteSymbols(replace_fst);
    (*new_pairs)[i + 1] = std::make_pair(kNoLabel, replace_fst);
  }
  // Now we set all non-initial replacement labels using the global symbol
  // table. As elsewhere in the library, output labels/symbols are used when
  // we have to choose just one table.
  for (size_t i = 0; i < size; ++i) {
    const auto nonterm = pairs[i].first;
    const auto idx = osyms->Find(nonterm);
    if (idx == kNoLabel) {
      FSTERROR() << "Replacement requested for unknown label: " << nonterm;
      return false;
    }
    (*new_pairs)[i + 1].first = static_cast<Label>(idx);
  }
  // Finally, we add the root FST to the RTN set, using kNoLabel as the root
  // label.
  auto *root_copy = new VectorFst<Arc>(root);
  root_copy->SetInputSymbols(isyms.get());
  root_copy->SetOutputSymbols(osyms.get());
  (*new_pairs)[0] = std::make_pair(kNoLabel, root_copy);
  return true;
}

template <class Arc>
inline void CleanUpNewPairs(
    std::vector<std::pair<typename Arc::Label, const Fst<Arc> *>> *new_pairs) {
  for (const auto &pair : *new_pairs) delete pair.second;
}

}  // namespace internal

// FST replacement.

template <class Arc>
void PyniniReplace(
    const Fst<Arc> &root,
    const std::vector<std::pair<string, const Fst<Arc> *>> &pairs,
    MutableFst<Arc> *ofst, ReplaceFstOptions<Arc> *opts) {
  const auto size = pairs.size();
  if (size < 1) {
    FSTERROR() << "PyniniReplace: Expected at least 1 replacement, "
               << "got " << size;
    ofst->SetProperties(kError, kError);
    return;
  }
  std::vector<std::pair<typename Arc::Label, const Fst<Arc> *>> new_pairs;
  if (!internal::PrepareReplacePairs(root, pairs, &new_pairs)) {
    ofst->SetProperties(kError, kError);
    return;
  }
  // Constructs and expands a ReplaceFst.
  opts->gc = true;
  opts->gc_limit = 0;
  ReplaceFst<Arc> rfst(new_pairs, *opts);
  if (rfst.CyclicDependencies()) {
    FSTERROR() << "Cyclic dependencies present in replacement set";
    ofst->SetProperties(kError, kError);
    return;
  }
  *ofst = rfst;  // Expands ReplaceFst into the output FST container.
  internal::CleanUpNewPairs(&new_pairs);
}

// PDT replacement.

template <class Arc>
void PyniniReplace(
    const Fst<Arc> &root,
    const std::vector<std::pair<string, const Fst<Arc> *>> &pairs,
    MutableFst<Arc> *ofst,
    std::vector<std::pair<typename Arc::Label, typename Arc::Label>> *parens,
    PdtParserType type = PDT_LEFT_PARSER) {
  using Label = typename Arc::Label;
  const auto size = pairs.size();
  if (size < 1) {
    FSTERROR() << "PyniniReplace: Expected at least 1 replacement, "
               << "got " << size;
    ofst->SetProperties(kError, kError);
    return;
  }
  std::vector<std::pair<typename Arc::Label, const Fst<Arc> *>> new_pairs;
  if (!internal::PrepareReplacePairs(root, pairs, &new_pairs)) {
    ofst->SetProperties(kError, kError);
    return;
  }
  // Performs PDT replacement.
  auto start_paren_labels = static_cast<Label>(
      new_pairs[0].second->OutputSymbols()
          ? new_pairs[0].second->OutputSymbols()->AvailableKey()
          : kNoLabel);
  // We use kNoLabel as the root label.
  PdtReplaceOptions<Arc> opts(kNoLabel, type, start_paren_labels);
  Replace(new_pairs, ofst, parens, opts);
  internal::CleanUpNewPairs(&new_pairs);
}

// Scripting API wrapper of the above.

namespace script {

using StringFstClassPair = std::pair<string, const FstClass *>;

using PyniniReplaceArgs =
    std::tuple<const FstClass &, const std::vector<StringFstClassPair> &,
               MutableFstClass *, const ReplaceOptions &>;

template <class Arc>
void PyniniReplace(PyniniReplaceArgs *args) {
  const Fst<Arc> &root = *(std::get<0>(*args).GetFst<Arc>());
  const auto &untyped_pairs = std::get<1>(*args);
  const size_t size = untyped_pairs.size();
  std::vector<std::pair<string, const Fst<Arc> *>> typed_pairs;
  typed_pairs.reserve(size);
  for (const auto &untyped_pair : untyped_pairs) {
    typed_pairs.emplace_back(untyped_pair.first,
                             untyped_pair.second->GetFst<Arc>());
  }
  MutableFst<Arc> *ofst = std::get<2>(*args)->GetMutableFst<Arc>();
  const ReplaceOptions &untyped_opts = std::get<3>(*args);
  ReplaceFstOptions<Arc> typed_opts(kNoLabel, untyped_opts.call_label_type,
                                    untyped_opts.return_label_type,
                                    untyped_opts.return_label);
  PyniniReplace(root, typed_pairs, ofst, &typed_opts);
}

void PyniniReplace(const FstClass &root,
                   const std::vector<StringFstClassPair> &pairs,
                   MutableFstClass *ofst, const ReplaceOptions &opts);

// PDT replacement.

using PyniniPdtReplaceArgs =
    std::tuple<const FstClass &, const std::vector<StringFstClassPair> &,
               MutableFstClass *, std::vector<LabelPair> *, PdtParserType>;

template <class Arc>
void PyniniPdtReplace(PyniniPdtReplaceArgs *args) {
  const Fst<Arc> &root = *(std::get<0>(*args).GetFst<Arc>());
  const auto &untyped_pairs = std::get<1>(*args);
  const size_t size = untyped_pairs.size();
  std::vector<std::pair<string, const Fst<Arc> *>> typed_pairs;
  typed_pairs.reserve(size);
  for (const auto &untyped_pair : untyped_pairs) {
    typed_pairs.emplace_back(untyped_pair.first,
                             untyped_pair.second->GetFst<Arc>());
  }
  MutableFst<Arc> *ofst = std::get<2>(*args)->GetMutableFst<Arc>();
  std::vector<std::pair<typename Arc::Label, typename Arc::Label>> typed_parens;
  PyniniReplace(root, typed_pairs, ofst, &typed_parens);
  // Copies parens back.
  std::get<3>(*args)->resize(typed_parens.size());
  std::copy(typed_parens.begin(), typed_parens.end(),
            std::get<3>(*args)->begin());
}

void PyniniPdtReplace(const FstClass &root,
                      const std::vector<StringFstClassPair> &pairs,
                      MutableFstClass *ofst, std::vector<LabelPair> *parens,
                      PdtParserType type = PDT_LEFT_PARSER);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_PYNINI_REPLACE_H_

