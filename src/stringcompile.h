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
#include <utility>
#include <vector>

#include <fst/types.h>
#include <fst/fst-decl.h>
#include <fst/icu.h>
#include <fst/properties.h>
#include <fst/string.h>

#include "gtl.h"

// This module contains a singleton class which can compile strings into string
// FSTs, keeping track of so-called generated labels.
//
// As this is a singleton class, the standard way to access it is to
// define:
//
//   static StringCompiler *compiler = StringCompiler::Get();
//
// Input strings can be compiled by viewing them as raw bytes (BYTE),
// sequences of UTF-8-encoded Unicode codepoints (UTF8), or as a sequence of
// symbols in a predefined symbol table, delimited by whitespace (SYMBOL).
//
// Both the BYTE and UTF8 modes treat strings enclosed in square brackets as
// "generated symbols". Generated symbols are stored within the compiler
// object in a hash map. They are assigned unique integral indices. These
// begin at 0xF0000, so if they are viewed as Unicode codepoints, they
// reside in the roughly 130,000 private code points in planes 15-16
// reserved for private use.
//
// The user can optionally attach a final weight to the resulting FST.
//
// This class also includes a const static method which returns a copy of
// a symbol table with the epsilon and the 95 printable ASCII characters.

namespace fst {

constexpr char kGeneratedSymbolsName[] = "**Generated symbols";
constexpr char kEpsilonString[] = "<epsilon>";

// Special handling for BOS and EOS markers in CDRewrite.
constexpr int64 kBosIndex = 0xF8FE;
constexpr int64 kEosIndex = 0xF8FF;
constexpr char kBosString[] = "BOS";
constexpr char kEosString[] = "EOS";

namespace internal {

// String compiler used by Pynini; used as a singleton.
class StringCompiler {
 public:
  static StringCompiler *Get() { return instance_; }

  // Extracts a list of labels from an string. If ttype = SYMBOL, then the
  // user must pass a symbol table used to label the string.
  template <class Label>
  bool StringToLabels(const std::string &str, std::vector<Label> *labels,
                      StringTokenType ttype = BYTE,
                      const SymbolTable *syms = nullptr) {
    if (ttype == BYTE || ttype == UTF8) {
      bool inside_brackets = false;
      std::string chunk;
      for (auto it = str.begin(); it != str.end(); ++it) {
        char ch = *it;
        if (*it == '[') {
          if (inside_brackets) {
            LOG(ERROR) << "StringToLabels: Unmatched [";
            return false;
          }
          if (!ProcessUnbracketedSpan(chunk, labels, ttype == BYTE)) {
            return false;
          }
          chunk.clear();
          inside_brackets = true;
        } else if (ch == ']') {
          if (!inside_brackets) {
            LOG(ERROR) << "StringToLabels: Unmatched ]";
            return false;
          }
          if (!ProcessBracketedSpan(chunk, labels)) return false;
          chunk.clear();
          inside_brackets = false;
        } else {
          if (ch == '\\') {
            if (++it == str.end()) {
              LOG(ERROR) << "StringToLabels: Unterminated escape";
              return false;
            } else {
              ch = *it;
            }
            switch (ch) {
              case 'n': {
                ch = '\n';
                break;
              }
              case 'r': {
                ch = '\r';
                break;
              }
              case 't': {
                ch = '\t';
                break;
              }
            }
          }
          chunk += ch;
        }
      }
      if (inside_brackets) {
        LOG(ERROR) << "StringToLabels: Unmatched [";
        return false;
      }
      return ProcessUnbracketedSpan(chunk, labels, ttype == BYTE);
    } else {  // ttype == SYMBOL
      for (const auto token : strings::Split(str, ' ')) {
        const Label label = syms->Find(token);
        if (label == kNoSymbol) {
          LOG(ERROR) << "SymbolStringToLabels: Symbol \"" << token << "\" "
                     << "is not mapped to any integer label in symbol table "
                     << syms->Name();
          return false;
        }
        labels->emplace_back(label);
      }
    }
    return true;
  }

  // This method combines parsing strings into labels (StringToLabels) and
  // compilation of labels into a string FST (LabelsToFst).
  //
  // If ttype = SYMBOL, then the user must pass a symbol table used to label
  // the string.
  template <class Arc>
  bool Compile(const std::string &str, MutableFst<Arc> *fst,
               StringTokenType ttype = BYTE, const SymbolTable *syms = nullptr,
               typename Arc::Weight weight = Arc::Weight::One()) {
    std::vector<typename Arc::Label> labels;
    if (!StringToLabels(str, &labels, ttype, syms)) return false;
    LabelsToFst(labels, fst, weight);
    return true;
  }

  // Returns a symbol table populated with the generated symbols. The caller
  // owns the pointer.
  SymbolTable *GeneratedSymbols() const;

 private:
  // Standard constructor is private; other constructors are deleted. This
  // enforces the desired singleton pattern.
  StringCompiler();
  StringCompiler(const StringCompiler &) = delete;
  StringCompiler &operator=(const StringCompiler &) = delete;

  int64 NumericalSymbolToLabel(const std::string &token) const;
  int64 StringSymbolToLabel(const std::string &token);
  int64 NumericalOrStringSymbolToLabel(const std::string &token);

  // Processes a BYTE or a UTF8 span inside brackets.
  template <class Label>
  bool ProcessBracketedSpan(const std::string &span,
                            std::vector<Label> *labels) {
    const std::vector<std::string> tokens(strings::Split(span, ' '));
    if (tokens.empty()) {
      LOG(ERROR) << "ProcessBracketedSpan: Empty span";
      return false;
    } else if (tokens.size() == 1) {
      // Both numerical string parsing modes are available if there is a
      // single element in the bracketed span.
      labels->emplace_back(NumericalOrStringSymbolToLabel(tokens[0]));
    } else {
      // Only string parsing is available if there are multiple elements in
      // the bracketed span.
      for (const auto &token : tokens) {
        labels->emplace_back(StringSymbolToLabel(token));
      }
    }
    return true;
  }

  // Processes a BYTE or a UTF8 span outside brackets.
  template <class Label>
  bool ProcessUnbracketedSpan(const std::string &span,
                              std::vector<Label> *labels, bool byte) {
    return byte ? ByteStringToLabels(span, labels)
                : UTF8StringToLabels(span, labels);
  }

  template <class Arc>
  void LabelsToFst(const std::vector<typename Arc::Label> &labels,
                   MutableFst<Arc> *fst,
                   typename Arc::Weight weight = Arc::Weight::One()) {
    using Weight = typename Arc::Weight;
    fst->DeleteStates();
    auto s = fst->AddState();
    fst->SetStart(s);
    fst->AddStates(labels.size());
    for (const auto label : labels) {
      fst->AddArc(s, Arc(label, label, s + 1));
      ++s;
    }
    auto props = kCompiledStringProperties;
    if (weight == Weight::One()) {
      fst->SetFinal(s);
    } else {
      fst->SetFinal(s, std::move(weight));
      props &= ~kUnweighted;
      props |= kWeighted;
    }
    fst->SetProperties(props, props);
  }

  // Map from generated symbols to labels.
  std::unordered_map<std::string, int64> gensyms_;
  // The highest-numbered generated symbol currently present.
  int64 max_gensym_;

  // The actual instance; access it with StringCompiler::Get().
  static StringCompiler *instance_;
};

}  // namespace internal

// The caller takes ownership.
SymbolTable *GeneratedSymbols();

// Convenience methods, to eliminate the need to call Get on the singleton.

template <class Label>
bool StringToLabels(const std::string &str, std::vector<Label> *labels,
                    StringTokenType ttype = BYTE,
                    const SymbolTable *syms = nullptr) {
  static auto *compiler = internal::StringCompiler::Get();
  return compiler->StringToLabels(str, labels, ttype, syms);
}

template <class Arc>
bool CompileString(const std::string &str, MutableFst<Arc> *fst,
                   StringTokenType ttype = BYTE,
                   const SymbolTable *syms = nullptr,
                   typename Arc::Weight weight = Arc::Weight::One()) {
  static auto *compiler = internal::StringCompiler::Get();
  return compiler->Compile(str, fst, ttype, syms, weight);
}

}  // namespace fst

#endif  // PYNINI_STRINGCOMPILE_H_

