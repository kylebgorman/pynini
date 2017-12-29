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

#include "stringfile.h"

#include <vector>

#include "stripcomment.h"
#include "gtl.h"
#include <re2/stringpiece.h>

namespace fst {
namespace internal {

void StringFile::Reset() {
  istrm_.clear();
  istrm_.seekg(0, istrm_.beg);
  Next();
}

void StringFile::Next() {
  // Reads a line; if it's empty, reads until it runs out of file or it finds a
  // non-empty one.
  ++linenum_;
  if (!ReadLineOrClear()) return;
  while (line_.empty()) {
    ++linenum_;
    if (!ReadLineOrClear()) return;
  }
}

bool StringFile::ReadLineOrClear() {
  if (!std::getline(istrm_, line_)) {
    line_.clear();
    return false;
  }
  line_ = StripCommentAndRemoveEscape(line_);
  return true;
}

bool PairStringFile::Parse() {
  std::vector<string> pieces = strings::Split(sf_.GetString(), "\t");
  if (pieces.size() != 2) return false;
  left_ = pieces[0];
  right_ = pieces[1];
  return true;
}

}  // namespace internal
}  // namespace fst

