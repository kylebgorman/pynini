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

#include <algorithm>
#include <memory>
#include <string>
using std::string;
#include <utility>

#include <fst/types.h>
#include <fst/fst-decl.h>
#include <fst/icu.h>
#include <fst/string.h>
#include "gtl.h"

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

// Symbol table support.

SymbolTable *GetByteSymbolTable();

SymbolTable *GetUTF8SymbolTable();

namespace internal {

constexpr char kDummySymbol[] = "PiningForTheFjords";

constexpr uint64 kCompiledStringProps = kAcceptor | kIDeterministic |
    kODeterministic | kILabelSorted | kOLabelSorted | kUnweighted | kAcyclic |
    kInitialAcyclic | kTopSorted | kAccessible | kCoAccessible | kString |
    kUnweightedCycles;

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

// Adds a Unicode codepoint to the symbol table. Returns kNoLabel to indicate
// that the input cannot be parsed as a Unicode codepoint.
int32 AddUnicodeCodepointToSymbolTable(int32 ch, SymbolTable *syms);

// String compilation helpers.

// Populates a string FST using a vector of labels.
template <class Arc>
void CompileFstFromLabels(
    const std::vector<typename Arc::Label> &labels, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One()) {
  using StateId = typename Arc::StateId;
  using Weight = typename Arc::Weight;
  fst->DeleteStates();
  fst->ReserveStates(labels.size());
  auto s = fst->AddState();
  fst->SetStart(s);
  for (const auto label : labels) {
    const auto nextstate = fst->AddState();
    fst->AddArc(s, Arc(label, label, Weight::One(), nextstate));
    s = nextstate;
  }
  fst->SetFinal(s, weight);
  fst->SetProperties(kCompiledStringProps, kCompiledStringProps);
}

// Parses a bracketed span.
int64 BracketedStringToLabel(const string &token, SymbolTable *syms);

// Processes the contents of a bracketed span.
template <class Label>
bool ProcessBracketedSpan(const string &str, std::vector<Label> *labels,
                          SymbolTable *syms) {
  const std::vector<string> tokens = strings::Split(str, ' ');
  if (tokens.empty()) {
    LOG(ERROR) << "ProcessBracketedSpan: Empty span";
    return false;
  } else if (tokens.size() == 1) {
    // We perform strtoll-style parsing if there is only one generated label.
    labels->emplace_back(BracketedStringToLabel(tokens[0], syms));
  } else {
    // Otherwise they are just treated as strings.
    for (const auto token : tokens) {
      labels->emplace_back(syms->AddSymbol(token));
    }
  }
  return true;
}

// Creates a vector of labels from a bracketed bytestring, updating the symbol
// table as it goes.
template <class Label, class Processor>
bool BracketedStringToLabels(const string &str, std::vector<Label> *labels,
                             SymbolTable *syms, const Processor &processor) {
  bool inside_brackets = false;
  // TODO(kbg): Consider using std::stringstream instead.
  string chunk = "";
  for (auto it = str.begin(); it != str.end(); ++it) {
    if (*it == '[') {
      if (inside_brackets) {
        LOG(ERROR) << "BracketedStringToLabels: Unmatched [";
        return false;
      }
      if (!processor(chunk, labels, syms)) return false;
      chunk.clear();
      inside_brackets = true;
    } else if (*it == ']') {
      if (!inside_brackets) {
        LOG(ERROR) << "BracketedStringToLabels: Unmatched ]";
        return false;
      }
      if (!ProcessBracketedSpan(chunk, labels, syms)) return false;
      chunk.clear();
      inside_brackets = false;
    } else {
      if (*it == '\\') {
        if (++it == str.end()) {
          LOG(ERROR) << "BracketedStringToLabels: Unterminated escape";
          return false;
        }
      }
      chunk += *it;
    }
  }
  if (inside_brackets) {
    LOG(ERROR) << "Unmatched [";
    return false;
  }
  return processor(chunk, labels, syms);
}

// Specializations of the above.

template <class Label>
bool BracketedByteStringToLabels(const string &str, std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const auto processor = [](const string &str,
                                   std::vector<Label> *labels, SymbolTable *) {
    return ByteStringToLabels(str, labels);
  };
  return BracketedStringToLabels(str, labels, syms, processor);
}

template <class Label>
bool BracketedUTF8StringToLabels(const string &str, std::vector<Label> *labels,
                                 SymbolTable *syms) {
  static const auto processor =
      [](const string &str, std::vector<Label> *labels, SymbolTable *syms) {
        if (!UTF8StringToLabels(str, labels)) return false;
        // Also check whether we need to add new Unicode symbols to the symbol
        // table.
        for (const auto label : *labels) {
          if (label > 255) {
            if (AddUnicodeCodepointToSymbolTable(label, syms) == kNoLabel) {
              return false;
            }
          }
        }
        return true;
      };
  return BracketedStringToLabels(str, labels, syms, processor);
}

// Creates a vector of labels from a bracketed string using a symbol table.
template <class Label>
bool SymbolStringToLabels(const string &str, const SymbolTable &syms,
                          std::vector<Label> *labels) {
  for (const auto token : strings::Split(str, ' ')) {
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

// Public API for string compilation.

// Compiles bytestring into string FST without bracket handling.
template <class Arc>
bool CompileByteString(const string &str, MutableFst<Arc> *fst,
                       const typename Arc::Weight &weight = Arc::Weight::One(),
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  labels.reserve(str.size());
  ByteStringToLabels(str, &labels);
  internal::CompileFstFromLabels<Arc>(labels, fst, weight);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(GetByteSymbolTable());
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles UTF-8 string into string FST without bracket handling.
template <class Arc>
bool CompileUTF8String(const string &str, MutableFst<Arc> *fst,
                       const typename Arc::Weight &weight = Arc::Weight::One(),
                       bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!UTF8StringToLabels(str, &labels)) return false;
  internal::CompileFstFromLabels(labels, fst, weight);
  if (attach_symbols) {
    std::unique_ptr<SymbolTable> syms(GetUTF8SymbolTable());
    // Adds any non-ASCII bytes to the symbol table.
    for (const auto label : labels) {
      internal::AddUnicodeCodepointToSymbolTable(label, syms.get());
    }
    internal::AssignSymbolsToFst(*syms, fst);
  }
  return true;
}

// Compiles symbol string into string FST using SymbolTable.
template <class Arc>
bool CompileSymbolString(
    const string &str, const SymbolTable &syms, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  if (!internal::SymbolStringToLabels(str, syms, &labels)) return false;
  internal::CompileFstFromLabels(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst(syms, fst);
  return true;
}

// Compiles bytestring into string FST with bracket handling.
template <class Arc>
bool CompileBracketedByteString(
    const string &str, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(GetByteSymbolTable());
  if (!internal::BracketedByteStringToLabels<Label>(str, &labels, syms.get())) {
    return false;
  }
  internal::CompileFstFromLabels(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst(*syms, fst);
  return true;
}

// Compiles UTF-8 string into string FST with bracket handling.
template <class Arc>
bool CompileBracketedUTF8String(
    const string &str, MutableFst<Arc> *fst,
    const typename Arc::Weight &weight = Arc::Weight::One(),
    bool attach_symbols = true) {
  using Label = typename Arc::Label;
  std::vector<Label> labels;
  std::unique_ptr<SymbolTable> syms(GetUTF8SymbolTable());
  if (!internal::BracketedUTF8StringToLabels(str, &labels, syms.get())) {
    return false;
  }
  internal::CompileFstFromLabels(labels, fst, weight);
  if (attach_symbols) internal::AssignSymbolsToFst(*syms, fst);
  return true;
}

// Parses string into labels.
template <class Label>
bool StringToLabels(const string &str, std::vector<Label> *labels,
                    StringTokenType ttype = BYTE, SymbolTable *syms = nullptr) {
  labels->clear();
  switch (ttype) {
    case BYTE:
      return internal::BracketedByteStringToLabels(str, labels, syms);
    case UTF8:
      return internal::BracketedUTF8StringToLabels(str, labels, syms);
    case SYMBOL:
      return internal::SymbolStringToLabels(str, *syms, labels);
  }
  return false;  // Unreachable.
}

template <class Arc>
bool CompileString(const string &str, MutableFst<Arc> *fst,
                   StringTokenType ttype = BYTE,
                   const SymbolTable *syms = nullptr,
                   const typename Arc::Weight &weight = Arc::Weight::One(),
                   bool attach_symbols = true) {
  switch (ttype) {
    case BYTE:
      return CompileBracketedByteString(str, fst, weight, attach_symbols);
    case UTF8:
      return CompileBracketedUTF8String(str, fst, weight, attach_symbols);
    case SYMBOL:
      return CompileSymbolString(str, *syms, fst, weight, attach_symbols);
  }
  return false;  // Unreachable.
}

}  // namespace fst

#endif  // PYNINI_STRINGCOMPILE_H_

