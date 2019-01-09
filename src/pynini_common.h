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

#ifndef PYNINI_PYNINI_COMMON_H_
#define PYNINI_PYNINI_COMMON_H_

// This header defines internal namespace utility functions.

#include <fst/fstlib.h>
#include "mergesymbols.h"

namespace fst {
namespace internal {

// Helpers for preparing FST symbol tables for context-dependent rewrite
// rule application and replacement.

// The caller owns the returned symbol table and should delete it (or capture
// it into a unique_ptr) to prevent leaks.
template <class Arc>
SymbolTable *PrepareInputSymbols(SymbolTable *syms, MutableFst<Arc> *fst) {
  bool relabel = false;
  auto *const new_syms = MergeSymbols(syms, fst->InputSymbols(), &relabel);
  if (!new_syms) return syms ? syms->Copy() : nullptr;
  if (relabel) Relabel(fst, new_syms, nullptr);
  return new_syms;
}

// The caller owns the returned symbol table and should delete it (or capture
// it into a unique_ptr) to prevent leaks.
template <class Arc>
SymbolTable *PrepareOutputSymbols(SymbolTable *syms, MutableFst<Arc> *fst) {
  bool relabel = false;
  auto *const new_syms = MergeSymbols(syms, fst->OutputSymbols(), &relabel);
  if (!new_syms) return syms ? syms->Copy() : nullptr;
  if (relabel) Relabel(fst, nullptr, new_syms);
  return new_syms;
}

// Removes both symbol tables.
template <class Arc>
void DeleteSymbols(MutableFst<Arc> *fst) {
  fst->SetInputSymbols(nullptr);
  fst->SetOutputSymbols(nullptr);
}

}  // namespace internal
}  // namespace fst

#endif  // PYNINI_PYNINI_COMMON_H_

