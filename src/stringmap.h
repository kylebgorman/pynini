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

#ifndef PYNINI_STRINGMAP_H_
#define PYNINI_STRINGMAP_H_

// This file contains functions for compiling FSTs from pairs of strings
// using a prefix tree.

#include <sstream>
#include <string>
using std::string;
#include <utility>
#include <vector>

#include <iostream>
#include <fst/fstlib.h>
#include "stringcompile.h"
#include "stringfile.h"
#include "prefix_tree.h"

namespace fst {
namespace internal {

// Helper class for constructing string maps.
template <class Arc>
class StringMapCompiler {
 public:
  using Label = typename Arc::Label;
  using Weight = typename Arc::Weight;

  explicit StringMapCompiler(StringTokenType itype = BYTE,
                             StringTokenType otype = BYTE,
                             const SymbolTable *isyms = nullptr,
                             const SymbolTable *osyms = nullptr)
      : itype_(itype),
        otype_(otype),
        isyms_(GetSymbolTable(itype_, isyms)),
        osyms_(GetSymbolTable(otype_, osyms)) {}

  bool Add(const string &istring, const string &ostring,
           const Weight &weight = Weight::One()) {
    if (!StringToLabels<Label>(istring, &ilabels_, itype_, isyms_.get())) {
      return false;
    }
    if (!StringToLabels<Label>(ostring, &olabels_, otype_, osyms_.get())) {
      return false;
    }
    ptree_.Add(ilabels_, olabels_, weight);
    return true;
  }

  // Also parses a weight string.
  bool Add(const string &istring, const string &ostring,
           const string &weight) {
    std::istringstream strm(weight);
    Weight w;
    strm >> w;
    if (!strm) {
      LOG(ERROR) << "StringMapCompiler::Add: Bad weight: " << weight;
      return false;
    }
    return Add(istring, ostring, w);
  }

  void Compile(MutableFst<Arc> *fst,
               bool attach_input_symbols = true,
               bool attach_output_symbols = true) const {
    ptree_.ToFst(fst);
    // Optionally attaches symbol tables.
    if (attach_input_symbols) fst->SetInputSymbols(isyms_.get());
    if (attach_output_symbols) fst->SetOutputSymbols(osyms_.get());
  }

 private:
  const StringTokenType itype_;
  const StringTokenType otype_;
  const std::unique_ptr<SymbolTable> isyms_;
  const std::unique_ptr<SymbolTable> osyms_;
  PrefixTree<Arc> ptree_;

  // Transient data.
  std::vector<Label> ilabels_;
  std::vector<Label> olabels_;
};

}  // namespace internal

// Compiles deterministic FST representing the union of the cross-product of
// pairs of weighted string cross-products from a TSV file of string triples.
template <class Arc>
bool CompileStringFile(const string &fname, MutableFst<Arc> *fst,
                       StringTokenType itype = BYTE,
                       StringTokenType otype = BYTE,
                       const SymbolTable *isyms = nullptr,
                       const SymbolTable *osyms = nullptr,
                       bool attach_input_symbols = true,
                       bool attach_output_symbols = true) {
  internal::StringMapCompiler<Arc> compiler(itype, otype, isyms, osyms);
  internal::ColumnStringFile csf(fname);
  if (csf.Done()) return false;  // File opening failed.
  for (; !csf.Done(); csf.Next()) {
    const auto &line = csf.Row();
    switch (line.size()) {
      case 1: {
        const string iostring(line[0]);
        if (!compiler.Add(iostring, iostring)) return false;
        break;
      }
      case 2: {
        if (!compiler.Add(string(line[0]), string(line[1]))) return false;
        break;
      }
      case 3: {
        if (!compiler.Add(string(line[0]), string(line[1]),
                          string(line[2]))) {
          return false;
        }
        break;
      }
      default: {
        LOG(ERROR) << "CompileStringFile: Ill-formed line "
                   << csf.LineNumber() << " in file "
                   << csf.Filename();
        return false;
      }
    }
  }
  compiler.Compile(fst, attach_input_symbols, attach_output_symbols);
  return true;
}

// Compiles deterministic FST representing the union of the cross-product of
// pairs of weighted string cross-products from a vector of vector of strings.
template <class Arc>
bool CompileStringMap(const std::vector<std::vector<string>> &lines,
                      MutableFst<Arc> *fst, StringTokenType itype = BYTE,
                      StringTokenType otype = BYTE,
                      const SymbolTable *isyms = nullptr,
                      const SymbolTable *osyms = nullptr,
                      bool attach_input_symbols = true,
                      bool attach_output_symbols = true) {
  internal::StringMapCompiler<Arc> compiler(itype, otype, isyms, osyms);
  for (const auto &line : lines) {
    switch (line.size()) {
      case 1: {
        if (!compiler.Add(line[0], line[0])) return false;
        break;
      }
      case 2: {
        if (!compiler.Add(line[0], line[1])) return false;
        break;
      }
      case 3: {
        if (!compiler.Add(line[0], line[1], line[2])) return false;
        break;
      }
      default: {
        LOG(ERROR) << "CompileStringMap: Ill-formed line";
        return false;
      }
    }
  }
  compiler.Compile(fst, attach_input_symbols, attach_output_symbols);
  return true;
}

}  // namespace fst

#endif  // PYNINI_STRINGMAP_H_

