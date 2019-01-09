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

#include <fst/script/fst-class.h>
#include <fst/script/script-impl.h>
#include "mergesymbolsscript.h"

namespace fst {
namespace script {

void MergeSymbols(MutableFstClass *fst1, MutableFstClass *fst2,
                  MergeSymbolsType mst) {
  if (!internal::ArcTypesMatch(*fst1, *fst2, "MergeSymbols")) return;
  MergeSymbolsArgs args(fst1, fst2, mst);
  Apply<Operation<MergeSymbolsArgs>>("MergeSymbols", fst1->ArcType(), &args);
}

REGISTER_FST_OPERATION(MergeSymbols, StdArc, MergeSymbolsArgs);
REGISTER_FST_OPERATION(MergeSymbols, LogArc, MergeSymbolsArgs);
REGISTER_FST_OPERATION(MergeSymbols, Log64Arc, MergeSymbolsArgs);

}  // namespace script
}  // namespace fst

