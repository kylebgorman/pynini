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

#include "stringcompile.h"

#include <cstdlib>

namespace fst {
namespace internal {

// The caller takes ownership.
SymbolTable *StringCompiler::GeneratedSymbols() const {
  auto *syms = new SymbolTable(kGeneratedSymbolsName);
  syms->AddSymbol(kEpsilonString);
  for (auto it = gensyms_.begin(); it != gensyms_.end(); ++it) {
    syms->AddSymbol(it->first, it->second);
  }
  return syms;
}

// Returns kNoLabel on failure.
int64 StringCompiler::NumericalSymbolToLabel(const std::string &token) const {
  const auto *ctoken = token.c_str();
  char *p;
  const auto label = strtol(ctoken, &p, 0);
  return p < ctoken + token.size() ? kNoLabel : label;
}

int64 StringCompiler::StringSymbolToLabel(const std::string &token) {
  // Is a single byte.
  if (token.size() == 1) return *token.c_str();
  // Special handling for BOS and EOS markers in CDRewrite.
  if (token == kBosString) return kBosIndex;
  if (token == kEosString) return kEosIndex;
  // General symbol lookup.
  const auto it_success = gensyms_.emplace(token, max_gensym_);
  // If insertion succeeded, we increment the max label.
  if (it_success.second) ++max_gensym_;
  return it_success.first->second;
}

// Tries numerical parsing first, and if that fails, treats it as a generated
// label.
int64 StringCompiler::NumericalOrStringSymbolToLabel(const std::string &token) {
  int64 label = NumericalSymbolToLabel(token);
  if (label == kNoLabel) label = StringSymbolToLabel(token);
  return label;
}

// We store generated symbol numbering in the private areas in planes 15-16.
// There are roughly 130,000 such code points in this area.
StringCompiler::StringCompiler() : max_gensym_(0xF0000) {}

// Actually instantiate the instance.
StringCompiler *StringCompiler::instance_ = new StringCompiler();

}  // namespace internal

// Convenience methods, to eliminate the need to call Get on the singleton.

// The caller takes ownership.
SymbolTable *GeneratedSymbols() {
  static auto *compiler = internal::StringCompiler::Get();
  return compiler->GeneratedSymbols();
}

}  // namespace fst

