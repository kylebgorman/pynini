// Copyright 2016-2020 Google LLC
//
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


#include "stringutil.h"

#include <fst/compat.h>
#include "gtl.h"

namespace fst {
namespace {

std::string StripComment(const std::string &line) {
  char prev_char = '\0';
  for (size_t i = 0; i < line.size(); ++i) {
    const char this_char = line[i];
    if (this_char == '#' && prev_char != '\\') {
      // Strips comment and any trailing whitespace.
      return std::string(fst::StripTrailingAsciiWhitespace(line.substr(0, i)));
    }
    prev_char = this_char;
  }
  return line;
}

std::string RemoveEscape(const std::string &line) {
  return strings::StringReplace(line, "\\#", "#", true);
}

}  // namespace

std::string StripCommentAndRemoveEscape(const std::string &line) {
  return RemoveEscape(StripComment(line));
}

std::string Escape(const std::string &str) {
  std::string result;
  result.reserve(str.size());
  for (char ch : str) {
    switch (ch) {
      case '[':
      case ']':
      case '\\':
        result.push_back('\\');
    }
    result.push_back(ch);
  }
  return result;
}

}  // namespace fst

