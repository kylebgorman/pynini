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

// This file contains implementations of untemplated internal functions for
// string compilation. Not all are declared in the corresponding header.

DEFINE_int32(generated_label_index_start, 0x100000,
             "The lowest index a generated label is assigned to.");

namespace fst {
namespace internal {

SymbolTable *GetSymbolTable(StringTokenType ttype, const SymbolTable *syms) {
  switch (ttype) {
    case SYMBOL: {
      return syms->Copy();
    }
    case BYTE: {
      return internal::byte_table_factory.GetTable();
    }
    case UTF8: {
      return internal::utf8_table_factory.GetTable();
    }
  }
  // Unreachable.
  return nullptr;
}

// Adds an integer to the symbol table; using a byte symbol when in byte range.
void AddIntegerToSymbolTable(int64 label, SymbolTable *syms) {
  if (0 <= label && label <= 256) return;
  std::stringstream sstrm;
  sstrm << label;
  syms->AddSymbol(sstrm.str(), label);
}

// Replicates functionality in the ICU library for determining whether the
// character type is control or whitespace. Specifically:
//
// if (u_charType(c) == U_CONTROL_CHAR ||
//     u_hasBinaryProperty(c, UCHAR_WHITE_SPACE) ||
//     u_hasBinaryProperty(c, UCHAR_POSIX_BLANK))
//
// This was extracted from nlp/grm/language/walker/util/function/symbols.cc.
inline bool IsUnicodeSpaceOrControl(int32 label) {
  switch (label) {
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
    case 10:
    case 11:
    case 12:
    case 13:
    case 14:
    case 15:
    case 16:
    case 17:
    case 18:
    case 19:
    case 20:
    case 21:
    case 22:
    case 23:
    case 24:
    case 25:
    case 26:
    case 27:
    case 28:
    case 29:
    case 30:
    case 31:
    case 32:
    case 127:
    case 128:
    case 129:
    case 130:
    case 131:
    case 132:
    case 133:
    case 134:
    case 135:
    case 136:
    case 137:
    case 138:
    case 139:
    case 140:
    case 141:
    case 142:
    case 143:
    case 144:
    case 145:
    case 146:
    case 147:
    case 148:
    case 149:
    case 150:
    case 151:
    case 152:
    case 153:
    case 154:
    case 155:
    case 156:
    case 157:
    case 158:
    case 159:
    case 160:
    case 5760:
    case 6158:
    case 8192:
    case 8193:
    case 8194:
    case 8195:
    case 8196:
    case 8197:
    case 8198:
    case 8199:
    case 8200:
    case 8201:
    case 8202:
    case 8232:
    case 8233:
    case 8239:
    case 8287:
    case 12288:
      return true;
    default:
      return false;
  }
}

// Adds a Unicode codepoint to the symbol table. Returns kNoLabel to indicate
// that the input cannot be parsed as a Unicode codepoint.
int32 AddUnicodeCodepointToSymbolTable(int32 label, SymbolTable *syms) {
  string label_string;
  // Creates a vector with just this label.
  std::vector<int32> labels = {label};
  if (LabelsToUTF8String(labels, &label_string)) {
    return static_cast<int32>(syms->AddSymbol(label_string, label));
  } else {
    LOG(ERROR) << "Unable to parse Unicode codepoint";
    return kNoLabel;
  }
}

// Removes backslashes acting as bracket escape characters (e.g. "\[").
void RemoveBracketEscapes(string *str) {
  static const RE2 left_bracket_escape(kEscapedLeftBracket);
  RE2::GlobalReplace(str, left_bracket_escape, R"([)");
  static const RE2 right_bracket_escape(kEscapedRightBracket);
  RE2::GlobalReplace(str, right_bracket_escape, R"(])");
}

}  // namespace internal
}  // namespace fst

