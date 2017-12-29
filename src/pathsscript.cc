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

#include "pathsscript.h"
#include <fst/script/fst-class.h>
#include <fst/script/script-impl.h>

namespace fst {
namespace script {

StringPathsClass::StringPathsClass(const FstClass &fst, StringTokenType itype,
                                   StringTokenType otype,
                                   const SymbolTable *isyms,
                                   const SymbolTable *osyms, bool rm_epsilon)
    : impl_(nullptr) {
  InitStringPathsClassArgs args(fst, itype, otype, isyms, osyms, rm_epsilon,
                                this);
  Apply<Operation<InitStringPathsClassArgs>>("InitStringPathsClass",
                                             fst.ArcType(), &args);
}

REGISTER_FST_OPERATION(InitStringPathsClass, StdArc, InitStringPathsClassArgs);
REGISTER_FST_OPERATION(InitStringPathsClass, LogArc, InitStringPathsClassArgs);
REGISTER_FST_OPERATION(InitStringPathsClass, Log64Arc,
                       InitStringPathsClassArgs);

}  // namespace script
}  // namespace fst

