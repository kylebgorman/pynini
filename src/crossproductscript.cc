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

#include "crossproductscript.h"
#include <fst/script/fst-class.h>
#include <fst/script/script-impl.h>

namespace fst {
namespace script {

void CrossProduct(const FstClass &ifst1, const FstClass &ifst2,
                  MutableFstClass *ofst,
                  const WeightClass &final_weight) {
  if (!internal::ArcTypesMatch(ifst1, ifst2, "CrossProduct") ||
      !internal::ArcTypesMatch(ifst2, *ofst, "CrossProduct") ||
      !ofst->WeightTypesMatch(final_weight, "CrossProduct")) {
    ofst->SetProperties(kError, kError);
    return;
  }
  CrossProductArgs args(ifst1, ifst2, ofst, final_weight);
  Apply<Operation<CrossProductArgs>>("CrossProduct", ofst->ArcType(), &args);
}

// Defaults final weight to semiring One.
void CrossProduct(const FstClass &ifst1, const FstClass &ifst2,
                  MutableFstClass *ofst) {
  if (!internal::ArcTypesMatch(ifst1, ifst2, "CrossProduct") ||
      !internal::ArcTypesMatch(ifst2, *ofst, "CrossProduct")) {
    ofst->SetProperties(kError, kError);
  }
  const WeightClass final_weight = WeightClass::One(ofst->WeightType());
  CrossProductArgs args(ifst1, ifst2, ofst, final_weight);
  Apply<Operation<CrossProductArgs>>("CrossProduct", ofst->ArcType(), &args);
}

REGISTER_FST_OPERATION(CrossProduct, StdArc, CrossProductArgs);
REGISTER_FST_OPERATION(CrossProduct, LogArc, CrossProductArgs);
REGISTER_FST_OPERATION(CrossProduct, Log64Arc, CrossProductArgs);

}  // namespace script
}  // namespace fst

