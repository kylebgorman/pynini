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

#include <vector>

#include "merge.h"

namespace fst {
namespace internal {

// TODO(kbg) Consider adding code for the special case where one table is a
// superset of another.
SymbolTable *MergeSymbols(const SymbolTable *syms1, const SymbolTable *syms2,
                          bool *relabel) {
  *relabel = false;
  // The flag overrides any work.
  if (!FLAGS_fst_compat_symbols) return nullptr;
  // If either symbol table is null, there's no reason to merge or reassign.
  if (!syms1 || !syms2) return nullptr;
  // If their checksums match, there's no reason to merge or reassign.
  if (syms1->LabeledCheckSum() == syms2->LabeledCheckSum()) return nullptr;
  auto *merged = syms1->Copy();
  for (SymbolTableIterator siter(*syms2); !siter.Done(); siter.Next()) {
    const auto s2_key = siter.Value();
    const auto &s2_sym = siter.Symbol();
    const auto s1_key = merged->Find(s2_sym);
    if (s1_key != SymbolTable::kNoSymbol && s1_key != s2_key) {
      *relabel = true;
      continue;
    }
    const auto &s1_sym = merged->Find(s2_key);
    if (s1_sym != "" && s1_sym != s2_sym) {
      merged->AddSymbol(s2_sym);
      *relabel = true;
    } else {
      merged->AddSymbol(s2_sym, s2_key);
    }
  }
  return merged;
}

}  // namespace internal
}  // namespace fst

