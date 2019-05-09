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

#ifndef PYNINI_STRINGPRINT_H_
#define PYNINI_STRINGPRINT_H_

#include <string>
using std::string;

#include <fst/fst-decl.h>
#include <fst/string.h>

namespace fst {

template <class Arc>
bool PrintString(const Fst<Arc> &fst, string *str, StringTokenType ttype = BYTE,
                 const SymbolTable *syms = nullptr) {
  const StringPrinter<Arc> printer(ttype, syms);
  return printer(fst, str);
}

}  // namespace fst

#endif  // PYNINI_STRINGPRINT_H_

