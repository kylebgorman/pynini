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

#ifndef PYNINI_STRINGCOMPILE_H_
#define PYNINI_STRINGCOMPILE_H_

#include <limits>
#include <memory>
#include <string>
using std::string;

#include <fst/types.h>
#include <cstdlib>
#include <fst/fst-decl.h>
#include <fst/string.h>
#include "gtl.h"
#include <re2/stringpiece.h>
#include <re2/re2.h>

// The user-facing functions in this class behave similar to the StringCompiler
// class, but add several additional functionalities.
//
// First, the compiler functions create a symbol table from the labels and
// assign this table to the resulting FST. The input strings are treated as
// raw bytes (CompileByteString), UTF-8 characters (CompileUTF8String), or
// symbols from a SymbolTable (CompileSymbolString).
//
// Secondly, the functions CompileBracketedByteString and
// CompileBracketedUTF8String treats strings enclosed within square brackets
// as generated symbols with labels beyond the range of the Unicode Basic
// Multilingual Plane.
//
// If a bracketed string contains multiple instances of the space character,
// the bracketed span is assumed to contain multiple generated symbols.
//
// Each such symbol is first input is passed to the C library function strtoll,
// which attempts to parse it as a signed long integer---it can handle octal,
// decimal, and hexadecimal strings, and will ignore any leading whitespace---
// it is treated as a raw integer (usually a byte). If this fails, however,
// each token in the bracketed span is treated as a "generated" symbol with a
// unique integer label and a string form given by its input bytes.
//
// Nesting of square brackets is disallowed.
//
// To pass a bracket literal when using the CompileBracket* functions, simply
// escape it with a preceding backslash.

DECLARE_int32(generated_label_index_start);

namespace fst {
namespace internal {

// "Special" byte-range symbols.

constexpr char kTokenSeparator[] = " ";
constexpr char kDummySymbol[] = "PiningForTheFjords";

// Symbol table names.

constexpr char kByteSymbolTableName[] = "**Byte symbols";
constexpr char kUTF8SymbolTableName[] = "**UTF8 symbols";

// Properties bits for a newly-compiled string FST.

constexpr uint64 kCompiledStringProps = kAcceptor | kIDeterministic |
    kODeterministic | kILabelSorted | kOLabelSorted | kUnweighted | kAcyclic |
    kInitialAcyclic | kTopSorted | kAccessible | kCoAccessible | kString |
    kUnweightedCycles;

constexpr char kPieces[] = R"(((?:(?:\\[\[\]])|(?:[^\[\]]))+)|)"
                           R"((?:\[((?:(?:\\[\[\]])|(?:[^\[\]]))+)\])|)"
                           R"((.+))";
constexpr char kEscapedLeftBracket[] = R"(\\\[)";
constexpr char kEscapedRightBracket[] = R"(\\\])";

// Helpers for creating a symbol table, initialized with just epsilon.

class SymbolTableFactory {
 public:
  explicit SymbolTableFactory(const string &name) : syms_(name) {
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
    // Space doesn't print very nice.
    syms_.AddSymbol("<SPACE>", 32);
    // Printable ASCII.
    for (auto ch = 33; ch < 127; ++ch) syms_.AddSymbol(string(1, ch), ch);
    // One last control character.
    syms_.AddSymbol("<DEL>", 0x7f);
    // Adds supra-ASCII characters as hexidecimal strings.
    for (int ch = 128; ch < 256; ++ch) {
      std::stringstream sstrm;
      sstrm << "<0x" << std::hex << ch << ">";
      syms_.AddSymbol(sstrm.str(), ch);
    }
    // This advances the next label for the one-argument form of AddSymbols
    // (used for user-generated symbols) to beyond the code points for the
    // Basic Multilingual Plane.
    syms_.AddSymbol(kDummySymbol, FLAGS_generated_label_index_start);
  }

  // The SymbolTable's p-impl is reference-counted, so a deep copy is not made
  // unless the strings used contain control characters or user-generated
  // symbols.
  SymbolTable *GetTable() const { return syms_.Copy(); }

 private:
  SymbolTable syms_;

  SymbolTableFactory(const SymbolTableFactory &) = delete;
  SymbolTableFactory &operator=(const SymbolTableFactory &) = delete;
};

static const SymbolTableFactory byte_table_factory(kByteSymbolTableName);

static const SymbolTableFactory utf8_table_factory(kUTF8SymbolTableName);

SymbolTable *GetSymbolTable(StringTokenType ttype, const SymbolTable *syms);

// Adds an integer to the symbol table.
void AddIntegerToSymbolTable(int64 ch, SymbolTable *syms);

// Adds a Unicode codepoint to the symbol table. Returns kNoLabel to indicate
// that the input cannot be parsed as a Unicode codepoint.
int32 AddUnicodeCodepointToSymbolTable(int32 ch, SymbolTable *syms);

// Adds a generated label to the table.
inline int64 AddGeneratedToSymbolTable(const string &str, SymbolTable *syms) {
  return syms->AddSymbol(str);
}

// Populates a string FST using a vector of labels.
template <class Arc>
void CompileStringFromLabels(const std::vector<typename Arc::Label> &labels,
                             const typename Arc::Weight &weight,
                             MutableFst<Arc> *fst) {
  using StateId = typename Arc::StateId;
  using Weight = typename Arc::Weight;
  fst->DeleteStates();
  const StateId size = labels.size();
  fst->ReserveStates(size);
  for (StateId i = 0; i < size; ++i) {
    fst->AddState();
    fst->AddArc(i, Arc(labels[i], labels[i], Weight::One(), i + 1));
  }
  fst->SetStart(0);
  fst->SetFinal(fst->AddState(), weight);
  fst->SetProperties(kCompiledStringProps, kCompiledStringProps);
}

// Removes backslashes acting as bracket escape characters (e.g. "\[").
void RemoveBracketEscapes(string *str);

// Processes the labels within a bracketed span.
template <class Label>
bool ProcessBracketedSpan(string *str, std::vector<Label> *labels,
                          SymbolTable *syms) {
  RemoveBracketEscapes(str);
  // Splits string on the token separator.
  std::vector<string> tokens = strings::Split(*str, kTokenSeparator);
  // The span may not be empty, so that is not considered here.
  if (tokens.size() == 1) {
    const auto cpptoken = tokens[0];
    // Has the same lifetime as cpptoken, so long as we don't mutate cpptoken.
    const auto *ctoken = cpptoken.c_str();
    // A bracketed span that does not contain the token-separator is processed
    // either as a numeric label (e.g., [32]), or if that fails, as a single
    // generated label.
    char *p;
    int64 label = strtol(ctoken, &p, 0);
    if (p < ctoken + strlen(ctoken)) {
      // Could not parse the entire string as a number, so it is treated as a
      // generated label.
      label = AddGeneratedToSymbolTable(cpptoken, syms);
    } else {
      AddIntegerToSymbolTable(label, syms);
    }
    labels->push_back(static_cast<Label>(label));
  } else {  // tokens.size() > 1.
    // A bracketed span with multiple token-separator-delimited intervals is
    // processed as a sequence of generated labels.
    for (const auto token : tokens) {
      labels->push_back(static_cast<Label>(
          AddGeneratedToSymbolTable(token, syms)));
    }
  }
  return true;
}

// Creates a vector of labels from a bracketed bytestring, updating the symbol
// table as it goes.
template <class Label>
bool BracketedByteStringToLabels(const string &str,
                                 std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const RE2 pieces(kPieces);
  string unbracketed;
  string bracketed;
  string error;
  re2::StringPiece strp(str);
  while (RE2::Consume(&strp, pieces, &unbracketed, &bracketed, &error)) {
    if (!error.empty()) {
      LOG(ERROR) << "BracketedByteStringToLabels: Unbalanced brackets";
      return false;
    } else if (!unbracketed.empty()) {
      RemoveBracketEscapes(&unbracketed);
      for (const auto label : unbracketed) {
        labels->push_back(static_cast<Label>(label));
      }
    } else if (!ProcessBracketedSpan<Label>(&bracketed, labels, syms)) {
      // A non-empty bracketed span.
      return false;
    }
  }
  return true;
}

// Creates a vector of labels from a bracketed UTF-8 string, updating the
// symbol table as it goes.
template <class Label>
bool BracketedUTF8StringToLabels(const string &str,
                                 std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const RE2 pieces(kPieces);
  string unbracketed;
  string bracketed;
  string error;
  re2::StringPiece strp(str);
  while (RE2::Consume(&strp, pieces, &unbracketed, &bracketed, &error)) {
    if (!error.empty()) {
      LOG(ERROR) << "BracketedUTF8StringToLabels: Unbalanced brackets";
      return false;
    } else if (!unbracketed.empty()) {
      RemoveBracketEscapes(&unbracketed);
      // Adds only the new unbracketed labels.
      auto i = labels->size();
      if (!UTF8StringToLabels(unbracketed, labels)) return false;
      for (; i < labels->size(); ++i) {
        AddUnicodeCodepointToSymbolTable(static_cast<Label>((*labels)[i]),
                                         syms);
      }
    } else if (!ProcessBracketedSpan<Label>(&bracketed, labels, syms)) {
      // A non-empty bracketed span.
      return false;
    }
  }
  return true;
}

// Creates a vector of labels from a bracketed string using a symbol table.
template <class Label>
bool SymbolStringToLabels(const string &str, const SymbolTable &syms,
                          std::vector<Label> *labels) {
  std::vector<string> tokens = strings::Split(str, kTokenSeparator);
  labels->reserve(tokens.size());
  for (const auto token : tokens) {
    const auto label = static_cast<Label>(syms.Find(token));
    if (label == SymbolTable::kNoSymbol) {
      LOG(ERROR) << "SymbolStringToLabels: Symbol \"" << token << "\" "
                 << "is not mapped to any integer label in symbol table "
                 << syms.Name();
      return false;
    }
    labels->push_back(label);
  }
  return true;
}

// Assigns symbol table to FST.
template <class Arc>
inline void AssignSymbolsToFst(const SymbolTable &syms, MutableFst<Arc> *fst) {
  fst->SetInputSymbols(&syms);
  fst->SetOutputSymbols(&syms);
}

// Compiles string from label and assigns symbols to FST.
template <class Arc>
inline void FinalizeBracketedString(std::vector<typename Arc::Label> *labels,
                                    const typename Arc::Weight &weight,
                                    const SymbolTable &syms,
                                    MutableFst<Arc> *fst) {
}

}  // namespace internal

// Compiles bytestring into string FST.
template <class Arc>
bool CompileByteString(const string &str,
                       const typename Arc::Weight &weight,
                       MutableFst<Arc> *fst,
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  labels.reserve(str.size());
  for (const auto ch : str) labels.push_back(static_cast<Label>(ch));
  internal::CompileStringFromLabels<Arc>(labels, weight, fst);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(internal::byte_table_factory.GetTable());
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles UTF-8 string into string FST.
template <class Arc>
bool CompileUTF8String(const string &str,
                       const typename Arc::Weight &weight,
                       MutableFst<Arc> *fst,
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!UTF8StringToLabels(str, &labels)) return false;
  internal::CompileStringFromLabels<Arc>(labels, weight, fst);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(internal::utf8_table_factory.GetTable());
    for (const auto label : labels) {
      internal::AddUnicodeCodepointToSymbolTable(label, syms.get());
    }
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles string into string FST using SymbolTable.
template <class Arc>
bool CompileSymbolString(const string &str,
                         const typename Arc::Weight &weight,
                         const SymbolTable &syms, MutableFst<Arc> *fst,
                         bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!internal::SymbolStringToLabels<Label>(str, syms, &labels)) return false;
  internal::CompileStringFromLabels<Arc>(labels, weight, fst);
  if (attach_symbols) internal::AssignSymbolsToFst(syms, fst);
  return true;
}

// Compiles (possibly) bracketed bytestring into string FST.
template <class Arc>
bool CompileBracketedByteString(const string &str,
                                const typename Arc::Weight &weight,
                                MutableFst<Arc> *fst,
                                bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(internal::byte_table_factory.GetTable());
  if (!internal::BracketedByteStringToLabels<Label>(str, &labels,
                                                    syms.get())) {
    return false;
  }
  internal::CompileStringFromLabels<Arc>(labels, weight, fst);
  if (attach_symbols) internal::AssignSymbolsToFst<Arc>(*syms, fst);
  return true;
}

// Compiles (possibly) bracketed UTF-8 string into string FST.
template <class Arc>
bool CompileBracketedUTF8String(const string &str,
                                const typename Arc::Weight &weight,
                                MutableFst<Arc> *fst,
                                bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(internal::utf8_table_factory.GetTable());
  if (!internal::BracketedUTF8StringToLabels<Label>(str, &labels,
                                                    syms.get())) {
    return false;
  }
  internal::CompileStringFromLabels<Arc>(labels, weight, fst);
  if (attach_symbols) internal::AssignSymbolsToFst<Arc>(*syms, fst);
  return true;
}

template <class Label>
bool StringToLabels(const string &str, StringTokenType ttype,
                    std::vector<Label> *labels, SymbolTable *syms = nullptr) {
  labels->clear();
  switch (ttype) {
    case BYTE:
      return internal::BracketedByteStringToLabels<Label>(str, labels, syms);
    case UTF8:
      return internal::BracketedUTF8StringToLabels<Label>(str, labels, syms);
    case SYMBOL:
      return internal::SymbolStringToLabels<Label>(str, *syms, labels);
  }
  return true;
}

template <class Arc>
bool CompileString(const string &str, const typename Arc::Weight &weight,
                   StringTokenType ttype, MutableFst<Arc> *fst,
                   const SymbolTable *syms = nullptr,
                   bool attach_symbols = true) {
  switch (ttype) {
    case BYTE:
      return CompileBracketedByteString(str, weight, fst, attach_symbols);
    case UTF8:
      return CompileBracketedUTF8String(str, weight, fst, attach_symbols);
    case SYMBOL:
      return CompileSymbolString(str, weight, *syms, fst, attach_symbols);
  }
  return true;
}

}  // namespace fst

#endif  // PYNINI_STRINGCOMPILE_H_

