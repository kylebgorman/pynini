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

#include "stringmapscript.h"
#include <fst/script/script-impl.h>

namespace fst {
namespace script {

bool StringFile(const string &fname, MutableFstClass *fst,
                StringTokenType itype, StringTokenType otype,
                const SymbolTable *isyms, const SymbolTable *osyms,
                bool attach_input_symbols, bool attach_output_symbols) {
  StringFileInnerArgs iargs(fname, fst, itype, otype, isyms, osyms,
                            attach_input_symbols, attach_output_symbols);
  StringFileArgs args(iargs);
  Apply<Operation<StringFileArgs>>("StringFile", fst->ArcType(), &args);
  return args.retval;
}

REGISTER_FST_OPERATION(StringFile, StdArc, StringFileArgs);
REGISTER_FST_OPERATION(StringFile, LogArc, StringFileArgs);
REGISTER_FST_OPERATION(StringFile, Log64Arc, StringFileArgs);

bool StringMap(const std::vector<std::vector<string>> &lines,
               MutableFstClass *fst, StringTokenType itype,
               StringTokenType otype, const SymbolTable *isyms,
               const SymbolTable *osyms, bool attach_input_symbols,
               bool attach_output_symbols) {
  StringMapInnerArgs iargs(lines, fst, itype, otype, isyms, osyms,
                           attach_input_symbols, attach_output_symbols);
  StringMapArgs args(iargs);
  Apply<Operation<StringMapArgs>>("StringMap", fst->ArcType(), &args);
  return args.retval;
}

REGISTER_FST_OPERATION(StringMap, StdArc, StringMapArgs);
REGISTER_FST_OPERATION(StringMap, LogArc, StringMapArgs);
REGISTER_FST_OPERATION(StringMap, Log64Arc, StringMapArgs);

}  // namespace script
}  // namespace fst

