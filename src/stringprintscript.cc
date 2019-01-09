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

#include "stringprintscript.h"

namespace fst {
namespace script {

bool PrintString(const FstClass &fst, string *str, StringTokenType ttype,
                 const SymbolTable *syms) {
  PrintStringInnerArgs iargs(fst, str, ttype, syms);
  PrintStringArgs args(iargs);
  Apply<Operation<PrintStringArgs>>("PrintString", fst.ArcType(), &args);
  return args.retval;
}

REGISTER_FST_OPERATION(PrintString, StdArc, PrintStringArgs);
REGISTER_FST_OPERATION(PrintString, LogArc, PrintStringArgs);
REGISTER_FST_OPERATION(PrintString, Log64Arc, PrintStringArgs);

}  // namespace script
}  // namespace fst

