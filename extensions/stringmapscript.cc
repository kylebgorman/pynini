// Copyright 2016-2020 Google LLC
//
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


#include "stringmapscript.h"

#include <fst/script/script-impl.h>

namespace fst {
namespace script {

bool StringFileCompile(const std::string &source, MutableFstClass *fst,
                       TokenType input_token_type, TokenType output_token_type,
                       const SymbolTable *input_symbols,
                       const SymbolTable *output_symbols) {
  StringFileCompileInnerArgs iargs(source, fst, input_token_type,
                                   output_token_type, input_symbols,
                                   output_symbols);
  StringFileCompileArgs args(iargs);
  Apply<Operation<StringFileCompileArgs>>("StringFileCompile", fst->ArcType(),
                                          &args);
  return args.retval;
}

REGISTER_FST_OPERATION_3ARCS(StringFileCompile, StringFileCompileArgs);

bool StringMapCompile(const std::vector<std::vector<std::string>> &lines,
                      MutableFstClass *fst, TokenType input_token_type,
                      TokenType output_token_type,
                      const SymbolTable *input_symbols,
                      const SymbolTable *output_symbols) {
  StringMapCompileInnerArgs1 iargs(lines, fst, input_token_type,
                                   output_token_type, input_symbols,
                                   output_symbols);
  StringMapCompileArgs1 args(iargs);
  Apply<Operation<StringMapCompileArgs1>>("StringMapCompile", fst->ArcType(),
                                          &args);
  return args.retval;
}

REGISTER_FST_OPERATION_3ARCS(StringMapCompile, StringMapCompileArgs1);

bool StringMapCompile(
    const std::vector<std::tuple<std::string, std::string, WeightClass>> &lines,
    MutableFstClass *fst, TokenType input_token_type,
    TokenType output_token_type, const SymbolTable *input_symbols,
    const SymbolTable *output_symbols) {
  StringMapCompileInnerArgs2 iargs(lines, fst, input_token_type,
                                   output_token_type, input_symbols,
                                   output_symbols);
  StringMapCompileArgs2 args(iargs);
  Apply<Operation<StringMapCompileArgs2>>("StringMapCompile", fst->ArcType(),
                                          &args);
  return args.retval;
}

REGISTER_FST_OPERATION_3ARCS(StringMapCompile, StringMapCompileArgs2);

}  // namespace script
}  // namespace fst

