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

#ifndef PYNINI_MERGESYMBOLS_H_
#define PYNINI_MERGESYMBOLS_H_

// Merges FST symbol tables and resolves labeling conflicts. The lowest-level
// function is MergeSymbols, which creates a merged table and signals when
// relabeling is necessary due to labeling conflicts. The remaining functions
// target pairs of FSTs rather than tables, assigning the merged tables back to
// the argument FSTs when needed.

#include <memory>

#include <fst/mutable-fst.h>
#include <fst/relabel.h>
#include <fst/symbol-table.h>

namespace fst {
namespace internal {

// Returns a symbol table merging the two argument symbol tables. Symbol/key
// pairs from the first table are never modified, but pairs from the second
// may be in the case of conflicts; if so, the boolean argument is set to
// true. As symbol tables are nullable, they are passed as const pointers
// rather than via const references.
SymbolTable *MergeSymbols(const SymbolTable *syms1, const SymbolTable *syms2,
                          bool *relabel);

// Specific implementations, not intended for client use.

template <class Arc>
void MergeInput(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2) {
  bool relabel = false;
  std::unique_ptr<SymbolTable> new_syms(
      MergeSymbols(fst1->InputSymbols(), fst2->InputSymbols(), &relabel));
  if (!new_syms) return;
  if (relabel) Relabel(fst2, new_syms.get(), nullptr);
  fst1->SetInputSymbols(new_syms.get());
  fst2->SetInputSymbols(new_syms.get());
}

template <class Arc>
void MergeOutput(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2) {
  bool relabel = false;
  std::unique_ptr<SymbolTable> new_syms(
      MergeSymbols(fst1->OutputSymbols(), fst2->OutputSymbols(), &relabel));
  if (!new_syms) return;
  if (relabel) Relabel(fst2, nullptr, new_syms.get());
  fst1->SetOutputSymbols(new_syms.get());
  fst2->SetOutputSymbols(new_syms.get());
}

template <class Arc>
void MergeInputOutput(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2) {
  MergeInput(fst1, fst2);
  MergeOutput(fst1, fst2);
}

template <class Arc>
void MergeInside(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2) {
  bool relabel = false;
  std::unique_ptr<SymbolTable> new_syms(
      MergeSymbols(fst1->OutputSymbols(), fst2->InputSymbols(), &relabel));
  if (!new_syms) return;
  if (relabel) Relabel(fst2, new_syms.get(), nullptr);
  fst1->SetOutputSymbols(new_syms.get());
  fst2->SetInputSymbols(new_syms.get());
}

template <class Arc>
void MergeOutside(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2) {
  bool relabel = false;
  std::unique_ptr<SymbolTable> new_syms(
      MergeSymbols(fst1->InputSymbols(), fst2->OutputSymbols(), &relabel));
  if (!new_syms) return;
  if (relabel) Relabel(fst2, nullptr, new_syms.get());
  fst1->SetInputSymbols(new_syms.get());
  fst2->SetOutputSymbols(new_syms.get());
}

}  // namespace internal

enum MergeSymbolsType {
  MERGE_INPUT,
  MERGE_OUTPUT,
  // Merges both input and output; should be enabled for union and
  // concatenation.
  MERGE_INPUT_OUTPUT,
  // Merges left output and right input tables; should be enabled for
  // composition, intersection, and difference.
  MERGE_INSIDE,
  // Merges left input and right output tables; should be enabled for
  // cross-product.
  MERGE_OUTSIDE
};

// This is the most generic merging function, and it is the one most clients
// should use. If the tables have symbol conflicts, the left FST is relabeled.
template <class Arc>
void MergeSymbols(MutableFst<Arc> *fst1, MutableFst<Arc> *fst2,
                  MergeSymbolsType mst) {
  switch (mst) {
    case MERGE_INPUT:
      internal::MergeInput(fst1, fst2);
      return;
    case MERGE_OUTPUT:
      internal::MergeOutput(fst1, fst2);
      return;
    case MERGE_INPUT_OUTPUT:
      internal::MergeInputOutput(fst1, fst2);
      return;
    case MERGE_INSIDE:
      internal::MergeInside(fst1, fst2);
      return;
    case MERGE_OUTSIDE:
      internal::MergeOutside(fst1, fst2);
      return;
  }
}

}  // namespace fst

#endif  // PYNINI_MERGESYMBOLS_H_

