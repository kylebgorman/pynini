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

#include <sstream>

#include <cstdlib>

// This file contains implementations of untemplated internal functions for
// string compilation. Not all are declared in the corresponding header.

namespace fst {

// Symbol table support.

SymbolTable *GetByteSymbolTable() {
  static const auto *const kFactory =
      new internal::SymbolTableFactory("**Byte symbols");
  return kFactory->GetTable();
}

SymbolTable *GetUTF8SymbolTable() {
  static const auto *const kFactory =
      new internal::SymbolTableFactory("**UTF8 symbols");
  return kFactory->GetTable();
}

namespace internal {

SymbolTableFactory::SymbolTableFactory(const std::string &name) : syms_(name) {
  // Label zero is reserved for epsilon.
  syms_.AddSymbol("<epsilon>", 0);
  // ASCII control characters.
  syms_.AddSymbol("<SOH>", 0x01);
  syms_.AddSymbol("<STX>", 0x02);
  syms_.AddSymbol("<ETX>", 0x03);
  syms_.AddSymbol("<EOT>", 0x04);
  syms_.AddSymbol("<ENQ>", 0x05);
  syms_.AddSymbol("<ACK>", 0x06);
  syms_.AddSymbol("<BEL>", 0x07);
  syms_.AddSymbol("<BS>", 0x08);
  syms_.AddSymbol("<HT>", 0x09);
  syms_.AddSymbol("<LF>", 0x0a);
  syms_.AddSymbol("<VT>", 0x0b);
  syms_.AddSymbol("<FF>", 0x0c);
  syms_.AddSymbol("<CR>", 0x0d);
  syms_.AddSymbol("<SO>", 0x0e);
  syms_.AddSymbol("<SI>", 0x0f);
  syms_.AddSymbol("<DLE>", 0x10);
  syms_.AddSymbol("<DC1>", 0x11);
  syms_.AddSymbol("<DC2>", 0x12);
  syms_.AddSymbol("<DC3>", 0x13);
  syms_.AddSymbol("<DC4>", 0x14);
  syms_.AddSymbol("<NAK>", 0x15);
  syms_.AddSymbol("<SYN>", 0x16);
  syms_.AddSymbol("<ETB>", 0x17);
  syms_.AddSymbol("<CAN>", 0x18);
  syms_.AddSymbol("<EM>", 0x19);
  syms_.AddSymbol("<SUB>", 0x1a);
  syms_.AddSymbol("<ESC>", 0x1b);
  syms_.AddSymbol("<FS>", 0x1c);
  syms_.AddSymbol("<GS>", 0x1d);
  syms_.AddSymbol("<RS>", 0x1e);
  syms_.AddSymbol("<US>", 0x1f);
  // Space doesn't print very nicely.
  syms_.AddSymbol("<SPACE>", 32);
  // Printable ASCII.
  for (auto ch = 33; ch < 127; ++ch) syms_.AddSymbol(std::string(1, ch), ch);
  // One last control character.
  syms_.AddSymbol("<DEL>", 0x7f);
  // Adds supra-ASCII bytes as hexadecimal strings.
  for (int ch = 128; ch < 256; ++ch) {
    std::stringstream sstrm;
    sstrm << "<0x" << std::hex << ch << ">";
    syms_.AddSymbol(sstrm.str(), ch);
  }
  // This advances the next label for the one-argument form of AddSymbols
  // (used for user-generated symbols) to beyond the code points for the
  // Basic Multilingual Plane.
  syms_.AddSymbol(kDummySymbol, kDummyIndex);
}

SymbolTable *GetSymbolTable(StringTokenType ttype, const SymbolTable *syms) {
  switch (ttype) {
    case SYMBOL: {
      return syms->Copy();
    }
    case BYTE: {
      return GetByteSymbolTable();
    }
    case UTF8: {
      return GetUTF8SymbolTable();
    }
  }
  return nullptr;  // Unreachable.
}

// Adds a Unicode codepoint to the symbol table. Returns kNoLabel to indicate
// that the input cannot be parsed as a Unicode codepoint.
int32 AddUnicodeCodepointToSymbolTable(int32 label, SymbolTable *syms) {
  std::string str;
  // Creates a vector with just this label.
  std::vector<int32> labels{label};
  if (LabelsToUTF8String(labels, &str)) {
    return static_cast<int32>(syms->AddSymbol(str, label));
  } else {
    LOG(ERROR) << "Unable to parse Unicode codepoint";
    return kNoLabel;
  }
}

int64 BracketedStringToLabel(const std::string &token, SymbolTable *syms) {
  const auto *ctoken = token.c_str();
  char *p;
  int64 label = strtol(ctoken, &p, 0);
  // Could not parse the entire string as a number so it is assumed to be
  // a generated label.
  if (p < ctoken + token.size()) {
    label = syms->AddSymbol(token);
    // Label is outside of byte range so we have to add it.
  } else if (label > 255) {
    std::stringstream sstrm;
    sstrm << label;
    syms->AddSymbol(sstrm.str(), label);
  }
  return label;
}

}  // namespace internal
}  // namespace fst

