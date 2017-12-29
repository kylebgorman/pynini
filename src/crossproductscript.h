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

#ifndef PYNINI_CROSSPRODUCTSCRIPT_H_
#define PYNINI_CROSSPRODUCTSCRIPT_H_

#include <fst/script/arg-packs.h>
#include <fst/script/fst-class.h>
#include "crossproduct.h"

namespace fst {
namespace script {

using CrossProductArgs = std::tuple<const FstClass &, const FstClass &,
                                    MutableFstClass *, const WeightClass &>;

template <class Arc>
void CrossProduct(CrossProductArgs *args) {
  const Fst<Arc> &ifst1 = *(std::get<0>(*args).GetFst<Arc>());
  const Fst<Arc> &ifst2 = *(std::get<1>(*args).GetFst<Arc>());
  MutableFst<Arc> *ofst = std::get<2>(*args)->GetMutableFst<Arc>();
  const typename Arc::Weight &final_weight =
      *(std::get<3>(*args).GetWeight<typename Arc::Weight>());
  CrossProduct(ifst1, ifst2, ofst, final_weight);
}

void CrossProduct(const FstClass &ifst1, const FstClass &ifst2,
                  MutableFstClass *ofst, const WeightClass &final_weight);

// Defaults final weight to semiring One.
void CrossProduct(const FstClass &ifst1, const FstClass &ifst2,
                  MutableFstClass *ofst);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_CROSSPRODUCTSCRIPT_H_

