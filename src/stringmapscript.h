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

#ifndef PYNINI_STRINGMAPSCRIPT_H_
#define PYNINI_STRINGMAPSCRIPT_H_

#include <string>
using std::string;
#include <utility>
#include <vector>

#include <fst/fstlib.h>
#include <fst/script/arg-packs.h>
#include <fst/script/fstscript.h>
#include "stringmap.h"

namespace fst {
namespace script {

using StringFileInnerArgs =
    std::tuple<const string &, MutableFstClass *, StringTokenType,
               StringTokenType, const SymbolTable *, const SymbolTable *, bool,
               bool>;

using StringFileArgs = WithReturnValue<bool, StringFileInnerArgs>;

template <class Arc>
void StringFile(StringFileArgs *args) {
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  args->retval = CompileStringFile(
      std::get<0>(args->args), fst, std::get<2>(args->args),
      std::get<3>(args->args), std::get<4>(args->args), std::get<5>(args->args),
      std::get<6>(args->args), std::get<7>(args->args));
}

bool StringFile(const string &fname, MutableFstClass *fst,
                StringTokenType itype = BYTE, StringTokenType otype = BYTE,
                const SymbolTable *isyms = nullptr,
                const SymbolTable *osyms = nullptr,
                bool attach_input_symbols = true,
                bool attach_output_symbols = true);

using StringMapInnerArgs =
    std::tuple<const std::vector<std::vector<string>> &, MutableFstClass *,
               StringTokenType, StringTokenType, const SymbolTable *,
               const SymbolTable *, bool, bool>;

using StringMapArgs = WithReturnValue<bool, StringMapInnerArgs>;

template <class Arc>
void StringMap(StringMapArgs *args) {
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  args->retval = CompileStringMap(
      std::get<0>(args->args), fst, std::get<2>(args->args),
      std::get<3>(args->args), std::get<4>(args->args), std::get<5>(args->args),
      std::get<6>(args->args), std::get<7>(args->args));
}

bool StringMap(const std::vector<std::vector<string>> &lines,
               MutableFstClass *fst, StringTokenType itype = BYTE,
               StringTokenType otype = BYTE, const SymbolTable *isyms = nullptr,
               const SymbolTable *osyms = nullptr,
               bool attach_input_symbols = true,
               bool attach_output_symbols = true);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_STRINGMAPSCRIPT_H_

