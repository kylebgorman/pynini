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

#ifndef PYNINI_LENIENTLYCOMPOSESCRIPT_H_
#define PYNINI_LENIENTLYCOMPOSESCRIPT_H_

#include <fst/script/arg-packs.h>
#include <fst/script/fst-class.h>
#include "lenientlycompose.h"

namespace fst {
namespace script {

using LenientlyComposeArgs =
    std::tuple<const FstClass &, const FstClass &, const FstClass &,
               MutableFstClass *, const ComposeOptions &>;

template <class Arc>
void LenientlyCompose(LenientlyComposeArgs *args) {
  const Fst<Arc> &ifst1 = *(std::get<0>(*args).GetFst<Arc>());
  const Fst<Arc> &ifst2 = *(std::get<1>(*args).GetFst<Arc>());
  const Fst<Arc> &sigma_star = *(std::get<2>(*args).GetFst<Arc>());
  MutableFst<Arc> *ofst = std::get<3>(*args)->GetMutableFst<Arc>();
  LenientlyCompose(ifst1, ifst2, sigma_star, ofst, std::get<4>(*args));
}

void LenientlyCompose(const FstClass &ifst1, const FstClass &ifst2,
                      const FstClass &sigma_star, MutableFstClass *ofst,
                      const ComposeOptions &copts = ComposeOptions());

}  // namespace script
}  // namespace fst

#endif  // PYNINI_LENIENTLYCOMPOSESCRIPT_H_

