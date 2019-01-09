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

#include "stringcompilescript.h"
#include <fst/script/script-impl.h>

namespace fst {
namespace script {

bool CompileString(const string &str, MutableFstClass *fst,
                   StringTokenType ttype, const SymbolTable *syms,
                   const WeightClass &weight, bool attach_symbols) {
  if (!fst->WeightTypesMatch(weight, "CompileSymbolString")) {
    fst->SetProperties(kError, kError);
    return false;
  }
  CompileStringInnerArgs iargs(str, fst, ttype, syms, weight, attach_symbols);
  CompileStringArgs args(iargs);
  Apply<Operation<CompileStringArgs>>("CompileString", fst->ArcType(), &args);
  return args.retval;
}

REGISTER_FST_OPERATION(CompileString, StdArc, CompileStringArgs);
REGISTER_FST_OPERATION(CompileString, LogArc, CompileStringArgs);
REGISTER_FST_OPERATION(CompileString, Log64Arc, CompileStringArgs);

}  // namespace script
}  // namespace fst

