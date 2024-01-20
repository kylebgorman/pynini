// Copyright 2016-2024 Google LLC
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

#ifndef PYNINI_STRINGPRINT_H_
#define PYNINI_STRINGPRINT_H_

#include <string>

#include <fst/fst-decl.h>
#include <fst/string.h>

namespace fst {

// Prints a string FST to a std::string.
template <class Arc>
bool StringPrint(const Fst<Arc> &fst, std::string *str,
                 TokenType token_type = TokenType::BYTE,
                 const SymbolTable *symbols = nullptr) {
  const StringPrinter<Arc> printer(token_type, symbols);
  return printer(fst, str);
}

// Same as above but overloaded to also compute the path weight.
template <class Arc>
bool StringPrint(const Fst<Arc> &fst, std::string *str,
                 typename Arc::Weight *weight,
                 TokenType token_type = TokenType::BYTE,
                 const SymbolTable *symbols = nullptr) {
  const StringPrinter<Arc> printer(token_type, symbols);
  return printer(fst, str, weight);
}

// Same as above but converts the weight to a float, for legacy compatibility.
template <class Arc>
bool StringPrint(const Fst<Arc> &fst, std::string *str, float *weight,
                 TokenType token_type = TokenType::BYTE,
                 const SymbolTable *symbols = nullptr) {
  typename Arc::Weight typed_weight;
  if (!StringPrint(fst, str, &typed_weight, token_type, symbols)) return false;
  *weight = typed_weight.Value();
  return true;
}

}  // namespace fst

#endif  // PYNINI_STRINGPRINT_H_

