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

StringPathIteratorClass::StringPathIteratorClass(const FstClass &fst,
                                                 StringTokenType itype,
                                                 StringTokenType otype,
                                                 const SymbolTable *isyms,
                                                 const SymbolTable *osyms)
    : impl_(nullptr) {
  InitStringPathIteratorClassArgs args(fst, itype, otype, isyms, osyms, this);
  Apply<Operation<InitStringPathIteratorClassArgs>>(
      "InitStringPathIteratorClass", fst.ArcType(), &args);
}

REGISTER_FST_OPERATION(InitStringPathIteratorClass, StdArc,
                       InitStringPathIteratorClassArgs);
REGISTER_FST_OPERATION(InitStringPathIteratorClass, LogArc,
                       InitStringPathIteratorClassArgs);
REGISTER_FST_OPERATION(InitStringPathIteratorClass, Log64Arc,
                       InitStringPathIteratorClassArgs);

}  // namespace script
}  // namespace fst

