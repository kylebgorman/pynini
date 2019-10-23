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
#include <tuple>
#include <utility>
#include <vector>

#include <fst/fstlib.h>
#include <fst/script/arg-packs.h>
#include <fst/script/fstscript.h>
#include <fst/script/weight-class.h>
#include "stringmap.h"

namespace fst {
namespace script {

using StringFileCompileInnerArgs =
    std::tuple<const std::string &, MutableFstClass *, StringTokenType,
               StringTokenType, const SymbolTable *, const SymbolTable *, bool,
               bool>;

using StringFileCompileArgs = WithReturnValue<bool, StringFileCompileInnerArgs>;

template <class Arc>
void StringFileCompile(StringFileCompileArgs *args) {
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  args->retval = StringFileCompile(
      std::get<0>(args->args), fst, std::get<2>(args->args),
      std::get<3>(args->args), std::get<4>(args->args), std::get<5>(args->args),
      std::get<6>(args->args), std::get<7>(args->args));
}

bool StringFileCompile(const std::string &source, MutableFstClass *fst,
                       StringTokenType itype = BYTE,
                       StringTokenType otype = BYTE,
                       const SymbolTable *isyms = nullptr,
                       const SymbolTable *osyms = nullptr,
                       bool attach_input_symbols = true,
                       bool attach_output_symbols = true);

using StringMapCompileInnerArgs1 =
    std::tuple<const std::vector<std::vector<std::string>> &, MutableFstClass *,
               StringTokenType, StringTokenType, const SymbolTable *,
               const SymbolTable *, bool, bool>;

using StringMapCompileArgs1 = WithReturnValue<bool, StringMapCompileInnerArgs1>;

template <class Arc>
void StringMapCompile(StringMapCompileArgs1 *args) {
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  args->retval = StringMapCompile(
      std::get<0>(args->args), fst, std::get<2>(args->args),
      std::get<3>(args->args), std::get<4>(args->args), std::get<5>(args->args),
      std::get<6>(args->args), std::get<7>(args->args));
}

using StringMapCompileInnerArgs2 = std::tuple<
    const std::vector<std::tuple<std::string, std::string, WeightClass>> &,
    MutableFstClass *, StringTokenType, StringTokenType, const SymbolTable *,
    const SymbolTable *, bool, bool>;

using StringMapCompileArgs2 = WithReturnValue<bool, StringMapCompileInnerArgs2>;

template <class Arc>
void StringMapCompile(StringMapCompileArgs2 *args) {
  std::vector<std::tuple<std::string, std::string, typename Arc::Weight>> lines;
  for (const auto &line : std::get<0>(args->args)) {
    const auto &istring = std::get<0>(line);
    const auto &ostring = std::get<1>(line);
    const auto &weight = *std::get<2>(line).GetWeight<typename Arc::Weight>();
    // NOTE: For correctness, we *could* verify that the weight of every one of
    // these arcs matches the weight used by fst, but this isn't strictly
    // necessary.
    lines.emplace_back(istring, ostring, weight);
  }
  MutableFst<Arc> *fst = std::get<1>(args->args)->GetMutableFst<Arc>();
  args->retval = StringMapCompile(
      lines, fst, std::get<2>(args->args), std::get<3>(args->args),
      std::get<4>(args->args), std::get<5>(args->args), std::get<6>(args->args),
      std::get<7>(args->args));
}

bool StringMapCompile(const std::vector<std::vector<std::string>> &lines,
                      MutableFstClass *fst, StringTokenType itype = BYTE,
                      StringTokenType otype = BYTE,
                      const SymbolTable *isyms = nullptr,
                      const SymbolTable *osyms = nullptr,
                      bool attach_input_symbols = true,
                      bool attach_output_symbols = true);

bool StringMapCompile(
    const std::vector<std::tuple<std::string, std::string, WeightClass>> &lines,
    MutableFstClass *fst, StringTokenType itype = BYTE,
    StringTokenType otype = BYTE, const SymbolTable *isyms = nullptr,
    const SymbolTable *osyms = nullptr, bool attach_input_symbols = true,
    bool attach_output_symbols = true);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_STRINGMAPSCRIPT_H_

