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

#ifndef PYNINI_STRINGCOMPILESCRIPT_H_
#define PYNINI_STRINGCOMPILESCRIPT_H_

#include <fst/script/arg-packs.h>
#include <fst/script/fst-class.h>
#include "stringcompile.h"

namespace fst {
namespace script {

using CompileStringInnerArgs =
    std::tuple<const string &, MutableFstClass *, StringTokenType,
               const SymbolTable *, const WeightClass &, bool>;

using CompileStringArgs = WithReturnValue<bool, CompileStringInnerArgs>;

template <class Arc>
void CompileString(CompileStringArgs *args) {
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  const typename Arc::Weight weight =
      *(std::get<4>(args->args).GetWeight<typename Arc::Weight>());
  args->retval =
      CompileString(std::get<0>(args->args), fst, std::get<2>(args->args),
                    std::get<3>(args->args), weight, std::get<5>(args->args));
}

// As is sometimes the case, there are fewer default arguments for the scripting
// API variant because we can't infer the underlying weight type.
bool CompileString(const string &str, MutableFstClass *fst,
                   StringTokenType ttype, const SymbolTable *syms,
                   const WeightClass &weight, bool attach_symbols = true);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_STRINGCOMPILESCRIPT_H_

