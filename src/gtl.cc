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
// Copyright 2016 and onwards Google, Inc.
//
// For general information on the Pynini grammar compilation library, see
// pynini.opengrm.org.

#include <numeric>

#include "gtl.h"

namespace strings {
namespace {

// Computes size of joined string.
size_t GetResultSize(const std::vector<std::string> &elements, size_t s_size) {
  const auto lambda = [](size_t partial, const std::string &right) {
    return partial + right.size();
  };
  return (std::accumulate(elements.begin(), elements.end(), 0, lambda) +
          s_size * (elements.size() - 1));
}

}  // namespace

// Joins a vector of strings on a given delimiter.
std::string Join(const std::vector<std::string> &elements,
                 const std::string &delim) {
  std::string result;
  if (elements.empty()) return result;
  size_t s_size = delim.size();
  result.reserve(GetResultSize(elements, s_size));
  auto it = elements.begin();
  result.append(it->data(), it->size());
  for (++it; it != elements.end(); ++it) {
    result.append(delim.data(), s_size);
    result.append(it->data(), it->size());
  }
  return result;
}

// Splits a string according to delimiter, skipping over consecutive
// delimiters.
std::vector<std::string> Split(const std::string &full, char delim) {
  size_t prev = 0;
  size_t found = full.find_first_of(delim);
  size_t size = found - prev;
  std::vector<std::string> result;
  if (size > 0) result.emplace_back(full.substr(prev, size));
  while (found != std::string::npos) {
    prev = found + 1;
    found = full.find_first_of(delim, prev);
    size = found - prev;
    if (size > 0) result.emplace_back(full.substr(prev, size));
  }
  return result;
}

}  // namespace strings
