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

#ifndef PYNINI_CONTAINMENTSCRIPT_H_
#define PYNINI_CONTAINMENTSCRIPT_H_

#include <fst/script/arg-packs.h>
#include <fst/script/fst-class.h>
#include "containment.h"

namespace fst {
namespace script {

using ContainmentArgs =
    std::tuple<const FstClass &, const FstClass &, MutableFstClass *>;

template <class Arc>
void Containment(ContainmentArgs *args) {
  const Fst<Arc> &ifst = *(std::get<0>(*args).GetFst<Arc>());
  const Fst<Arc> &sigma_star = *(std::get<1>(*args).GetFst<Arc>());
  MutableFst<Arc> *ofst = std::get<2>(*args)->GetMutableFst<Arc>();
  Containment(ifst, sigma_star, ofst);
}

void Containment(const FstClass &ifst, const FstClass &sigma_star,
                 MutableFstClass *ofst);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_CONTAINMENTSCRIPT_H_

