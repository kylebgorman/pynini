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

SymbolTable *GetByteSymbolTable();

SymbolTable *GetUTF8SymbolTable();

namespace internal {

// "Special" byte-range symbols.

constexpr char kTokenSeparator[] = " ";
constexpr char kDummySymbol[] = "PiningForTheFjords";

// Symbol table names.

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

// Helpers for creating a symbol table.
class SymbolTableFactory {
 public:
  explicit SymbolTableFactory(const string &name);

  // The SymbolTable's p-impl is reference-counted, so a deep copy is not made
  // unless the strings used contain control characters or user-generated
  // symbols.
  SymbolTable *GetTable() const { return syms_.Copy(); }

 private:
  SymbolTable syms_;

  SymbolTableFactory(const SymbolTableFactory &) = delete;
  SymbolTableFactory &operator=(const SymbolTableFactory &) = delete;
};

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
void CompileStringFromLabels(
    const std::vector<typename Arc::Label> &labels, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One()) {
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
  const std::vector<string> tokens = strings::Split(*str, kTokenSeparator);
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
      labels->push_back(static_cast<Label>(AddGeneratedToSymbolTable(token,
                                                                     syms)));
    }
  }
  return true;
}

// Creates a vector of labels from a bracketed bytestring, updating the symbol
// table as it goes.
template <class Label>
bool BracketedByteStringToLabels(const string &strp,
                                 std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const RE2 pieces(kPieces);
  re2::StringPiece view(strp);
  string unbracketed;
  string bracketed;
  string error;
  while (RE2::Consume(&view, pieces, &unbracketed, &bracketed, &error)) {
    if (!error.empty()) {
      LOG(ERROR) << "BracketedByteStringToLabels: Unbalanced brackets";
      return false;
    } else if (!unbracketed.empty()) {
      RemoveBracketEscapes(&unbracketed);
      for (const char label : unbracketed) {
        labels->push_back(static_cast<unsigned char>(label));
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
bool BracketedUTF8StringToLabels(const string &strp, std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const RE2 pieces(kPieces);
  re2::StringPiece view(strp);
  string unbracketed;
  string bracketed;
  string error;
  while (RE2::Consume(&view, pieces, &unbracketed, &bracketed, &error)) {
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
bool SymbolStringToLabels(const string &strp, const SymbolTable &syms,
                          std::vector<Label> *labels) {
  for (const auto token : strings::Split(strp, kTokenSeparator)) {
    const auto label = static_cast<Label>(syms.Find(string(token)));
    if (label == kNoSymbol) {
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

}  // namespace internal

// Compiles bytestring into string FST.
template <class Arc>
bool CompileByteString(const string &strp, MutableFst<Arc> *fst,
                       const typename Arc::Weight &weight = Arc::Weight::One(),
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  labels.reserve(strp.size());
  for (const char ch : strp) {
    labels.push_back(static_cast<unsigned char>(ch));
  }
  internal::CompileStringFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(GetByteSymbolTable());
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles UTF-8 string into string FST.
template <class Arc>
bool CompileUTF8String(const string &strp, MutableFst<Arc> *fst,
                       const typename Arc::Weight &weight = Arc::Weight::One(),
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!UTF8StringToLabels(strp, &labels)) return false;
  internal::CompileStringFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(GetUTF8SymbolTable());
    for (const auto label : labels) {
      internal::AddUnicodeCodepointToSymbolTable(label, syms.get());
    }
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles string into string FST using SymbolTable.
template <class Arc>
bool CompileSymbolString(
    const string &strp, const SymbolTable &syms, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!internal::SymbolStringToLabels<Label>(strp, syms, &labels)) return false;
  internal::CompileStringFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst(syms, fst);
  return true;
}

// Compiles (possibly) bracketed bytestring into string FST.
template <class Arc>
bool CompileBracketedByteString(
    const string &strp, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(GetByteSymbolTable());
  if (!internal::BracketedByteStringToLabels<Label>(strp, &labels,
                                                    syms.get())) {
    return false;
  }
  internal::CompileStringFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst<Arc>(*syms, fst);
  return true;
}

// Compiles (possibly) bracketed UTF-8 string into string FST.
template <class Arc>
bool CompileBracketedUTF8String(
    const string &strp, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(GetUTF8SymbolTable());
  if (!internal::BracketedUTF8StringToLabels<Label>(strp, &labels,
                                                    syms.get())) {
    return false;
  }
  internal::CompileStringFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst<Arc>(*syms, fst);
  return true;
}

template <class Label>
bool StringToLabels(const string &strp, std::vector<Label> *labels,
                    StringTokenType ttype = BYTE, SymbolTable *syms = nullptr) {
  labels->clear();
  switch (ttype) {
    case BYTE:
      return internal::BracketedByteStringToLabels<Label>(strp, labels, syms);
    case UTF8:
      return internal::BracketedUTF8StringToLabels<Label>(strp, labels, syms);
    case SYMBOL:
      return internal::SymbolStringToLabels<Label>(strp, *syms, labels);
  }
  return true;
}

template <class Arc>
bool CompileString(const string &strp, MutableFst<Arc> *fst,
                   StringTokenType ttype = BYTE,
                   const SymbolTable *syms = nullptr,
                   const typename Arc::Weight &weight = Arc::Weight::One(),
                   bool attach_symbols = true) {
  switch (ttype) {
    case BYTE:
      return CompileBracketedByteString(strp, fst, weight, attach_symbols);
    case UTF8:
      return CompileBracketedUTF8String(strp, fst, weight, attach_symbols);
    case SYMBOL:
      return CompileSymbolString(strp, *syms, fst, weight, attach_symbols);
  }
  return true;
}

}  // namespace fst

#endif  // PYNINI_STRINGCOMPILE_H_

