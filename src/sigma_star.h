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

#ifndef PYNINI_SIGMA_STAR_H_
#define PYNINI_SIGMA_STAR_H_

#include <fst/fstlib.h>

namespace fst {
namespace internal {

// Checks that a "sigma_star" FST is an unweighted cyclic acceptor.
template <class Arc>
bool CheckSigmaStarProperties(const Fst<Arc> &sigma_star,
                              const string &op_name) {
  static constexpr auto props = kAcceptor | kUnweighted;
  if (sigma_star.Properties(props, true) != props) {
    LOG(ERROR) << op_name << ": sigma_star must be a unweighted "
               << "acceptor";
    return false;
  }
  return true;
}

}  // namespace internal
}  // namespace fst

#endif  // PYNINI_SIGMA_STAR_H_

