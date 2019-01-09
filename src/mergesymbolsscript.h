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

#ifndef PYNINI_MERGESYMBOLSSCRIPT_H_
#define PYNINI_MERGESYMBOLSSCRIPT_H_

#include <fst/script/arg-packs.h>
#include <fst/script/fst-class.h>
#include "mergesymbols.h"

namespace fst {
namespace script {

// These operations merge FST-attached symbol tables so that they are
// compatible for other FST operations.

using MergeSymbolsArgs = std::tuple<MutableFstClass *,
    MutableFstClass *, MergeSymbolsType>;

template <class Arc>
void MergeSymbols(MergeSymbolsArgs *args) {
  MutableFst<Arc> *fst1 = std::get<0>(*args)->GetMutableFst<Arc>();
  MutableFst<Arc> *fst2 = std::get<1>(*args)->GetMutableFst<Arc>();
  MergeSymbols(fst1, fst2, std::get<2>(*args));
}

void MergeSymbols(MutableFstClass *fst1, MutableFstClass *fst2,
                  MergeSymbolsType mst);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_MERGESYMBOLSSCRIPT_H_

