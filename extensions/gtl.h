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

#ifndef PYNINI_GTL_H_
#define PYNINI_GTL_H_

#include <string>
#include <utility>

// Prefix tree stuff.

template <class T>
void MapUtilAssignNewDefaultInstance(T **location) {
  *location = new T();
}

template <class T>
typename T::value_type::second_type LookupOrInsertNew(T * const collection,
    const typename T::value_type::first_type &key) {
  auto result = collection->insert(typename T::value_type(key,
      static_cast<typename T::value_type::second_type>(nullptr)));
  if (result.second) MapUtilAssignNewDefaultInstance(&(result.first->second));
  return result.first->second;
}

// Strings stuff.

namespace strings {
namespace internal {

inline void StringReplace(std::string *full, const std::string &before,
                          const std::string &after) {
  size_t pos = 0;
  while ((pos = full->find(before, pos)) != std::string::npos) {
    full->replace(pos, before.size(), after);
    pos += after.size();
  }
}
}  // namespace internal

inline std::string StringReplace(const std::string &full,
                                 const std::string &before,
                                 const std::string &after, bool /* ignored */) {
  std::string copy(full);
  internal::StringReplace(&copy, before, after);
  return copy;
}
}  // namespace strings

#endif  // PYNINI_GTL_H_
