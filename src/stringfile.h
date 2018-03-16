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
#include <vector>

#include <iostream>
#include <fst/fstlib.h>
#include "stringcompile.h"

namespace fst {
namespace internal {

// Basic line-by-line file iterator, with support for line numbers and
// \# comment stripping.
class StringFile {
 public:
  // Opens a file input stream using the provided filename.
  explicit StringFile(const string &fname)
      : istrm_(fname), linenum_(0), fname_(fname) {
     if (!!istrm_) Next();
  }

  void Reset();

  void Next();

  bool Done() const { return !istrm_ || istrm_.eof(); }

  const string &GetString() const { return line_; }

  size_t LineNumber() const { return linenum_; }

  const string &Filename() const { return fname_; }

 private:
  std::ifstream istrm_;
  string line_;
  size_t linenum_;
  const string fname_;
};

// File iterator expecting multiple columns separated by tab.
class ColumnStringFile {
 public:
  explicit ColumnStringFile(const string &fname)
      : sf_(fname) {
    Parse();
  }

  void Reset();

  void Next();

  bool Done() const { return sf_.Done(); }

  // Access to the underlying row vector.
  const std::vector<string> Row() const { return row_; }

  size_t LineNumber() const { return sf_.LineNumber(); }

  const string &Filename() const { return sf_.Filename(); }

 private:
  void Parse() { row_ = strings::Split(sf_.GetString(), "\t"); }

  StringFile sf_;
  std::vector<string> row_;
};

}  // namespace internal

}  // namespace fst

#endif  // PYNINI_STRINGFILE_H_

