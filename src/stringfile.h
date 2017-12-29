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

#ifndef PYNINI_STRINGFILE_H_
#define PYNINI_STRINGFILE_H_

#include <istream>
#include <string>
using std::string;
#include <utility>

#include <fst/fstlib.h>
#include "stringcompile.h"
#include <re2/stringpiece.h>

namespace fst {
namespace internal {

// Basic line-by-line file iterator.

class StringFile {
 public:
  StringFile(std::istream &istrm, const string &fname)  // NOLINT
      : istrm_(istrm), linenum_(0), fname_(fname) {
    Next();
  }

  void Reset();

  void Next();

  bool Done() const { return istrm_.eof() && line_.empty(); }

  const string &GetString() const { return line_; }

  size_t LineNumber() const { return linenum_; }

  const string &Filename() const { return fname_; }

 private:
  bool ReadLineOrClear();

  std::istream &istrm_;
  string line_;
  size_t linenum_;
  const string fname_;
};

// File iterator expecting two strings separated by a tab on each line.

class PairStringFile {
 public:
  PairStringFile(std::istream &istrm, const string &fname)  // NOLINT
      : sf_(istrm, fname) {
    Parse();
  }

  void Reset() {
    sf_.Reset();
    Parse();
  }

  void Next() {
    sf_.Next();
    while (!Parse() && !Done()) {
      LOG(WARNING) << "PairStringFile::Next: Skipping ill-formed line "
                   << sf_.LineNumber() << " in file " << sf_.Filename();
      sf_.Next();
      Parse();
    }
  }

  bool Done() const { return sf_.Done(); }

  const string GetLeftString() const { return left_; }

  const string GetRightString() const { return right_; }

  size_t LineNumber() const { return sf_.LineNumber(); }

  const string &Filename() const { return sf_.Filename(); }

 private:
  bool Parse();

  StringFile sf_;
  string left_;
  string right_;
};

}  // namespace internal

template <class Arc>
class FstStringFile {
 public:
  using Weight = typename Arc::Weight;

  FstStringFile(std::istream &istrm,  // NOLINT
                const string &fname, StringTokenType ttype,
                const SymbolTable *syms = nullptr)
      : sf_(istrm, fname), ttype_(ttype), syms_(syms) {
    Parse();
  }

  void Reset() {
    sf_.Reset();
    Parse();
  }

  void Next() {
    sf_.Next();
    if (!Parse() && !Done()) {
      LOG(WARNING) << "FstStringFile::Next: Skipping ill-formed line "
                   << sf_.LineNumber() << " in file " << sf_.Filename();
      sf_.Next();
      Parse();
    }
  }

  bool Done() const { return sf_.Done(); }

  const VectorFst<Arc> *GetFst() const { return &fst_; }

  const string &Filename() const { return sf_.Filename(); }

  size_t LineNumber() const { return sf_.LineNumber(); }

 private:
  bool Parse() {
    return CompileString(sf_.GetString(), Weight::One(), ttype_, &fst_, syms_);
  }

  internal::StringFile sf_;
  StringTokenType ttype_;
  const SymbolTable *syms_;
  VectorFst<Arc> fst_;
};

// File iterator that compiles each line as two string FSTs separated by a
// single tab character.

template <class Arc>
class PairFstStringFile {
 public:
  using Weight = typename Arc::Weight;

  PairFstStringFile(std::istream &istrm,  // NOLINT
                    const string &fname, StringTokenType itype,
                    StringTokenType otype, const SymbolTable *isyms = nullptr,
                    const SymbolTable *osyms = nullptr)
      : psf_(istrm, fname),
        itype_(itype),
        otype_(otype),
        isyms_(isyms),
        osyms_(osyms) {
    Parse();
  }

  void Reset() {
    psf_.Reset();
    Parse();
  }

  void Next() {
    psf_.Next();
    while (!Parse() && !Done()) {
      LOG(WARNING) << "PairFstStringFile::Next: Skipping ill-formed line "
                   << LineNumber() << " in file " << Filename();
      psf_.Next();
    }
  }

  bool Done() const { return psf_.Done(); }

  const VectorFst<Arc> *GetLeftFst() const { return &left_; }

  const VectorFst<Arc> *GetRightFst() const { return &right_; }

  const string &Filename() const { return psf_.Filename(); }

  size_t LineNumber() const { return psf_.LineNumber(); }

 private:
  bool Parse() {
    return CompileString(psf_.GetLeftString(), Weight::One(), itype_, &left_,
                         isyms_) &&
           CompileString(psf_.GetRightString(), Weight::One(), otype_, &right_,
                         osyms_);
  }

  internal::PairStringFile psf_;
  StringTokenType itype_;
  StringTokenType otype_;
  const SymbolTable *isyms_;
  const SymbolTable *osyms_;
  VectorFst<Arc> left_;
  VectorFst<Arc> right_;
};

}  // namespace fst

#endif  // PYNINI_STRINGFILE_H_

