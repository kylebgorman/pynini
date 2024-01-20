// Copyright 2016-2024 Google LLC
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

#include "getters.h"

#include "cdrewrite.h"
#include <string_view>

namespace fst {
namespace script {

bool GetCDRewriteDirection(std::string_view str, CDRewriteDirection *rd) {
  if (str == "ltr") {
    *rd = CDRewriteDirection::LEFT_TO_RIGHT;
  } else if (str == "rtl") {
    *rd = CDRewriteDirection::RIGHT_TO_LEFT;
  } else if (str == "sim") {
    *rd = CDRewriteDirection::SIMULTANEOUS;
  } else {
    return false;
  }
  return true;
}

bool GetCDRewriteMode(std::string_view str, CDRewriteMode *rm) {
  if (str == "obl") {
    *rm = CDRewriteMode::OBLIGATORY;
  } else if (str == "opt") {
    *rm = CDRewriteMode::OPTIONAL;
  } else {
    return false;
  }
  return true;
}

}  // namespace script
}  // namespace fst

