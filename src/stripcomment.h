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

#ifndef PYNINI_STRIPCOMMENT_H_
#define PYNINI_STRIPCOMMENT_H_

#include <string>
using std::string;


#include "gtl.h"

// Defines comment syntax for string files.
//
// The comment character is '#', and has scope until the end of the line. Any
// preceding whitespace before a comment is ignored.
//
// To use the '#' literal (i.e., to ensure it is not interpreted as the start of
// a comment) escape it with '\'; the escaping '\' in "\#" also removed.
//
// TODO(rws,kbg): Merge stringfile functionality across Pynini and Thrax.

namespace fst {
namespace internal {

inline string StripComment(const string &line) {
  char prev_char = '\0';
  for (size_t i = 0; i < line.size(); ++i) {
    const char this_char = line[i];
    if (this_char == '#' && prev_char != '\\') {
      // Strips comment and any trailing whitespace.
      return string(strings::StripTrailingAsciiWhitespace(line.substr(0, i)));
    }
    prev_char = this_char;
  }
  return line;
}

inline string RemoveEscape(const string &line) {
  return strings::StringReplace(StripComment(line), "\\#", "#", true);
}

}  // namespace internal

inline string StripCommentAndRemoveEscape(const string &line) {
  return internal::RemoveEscape(internal::StripComment(line));
}

}  // namespace fst

#endif  // PYNINI_STRIPCOMMENT_H_

