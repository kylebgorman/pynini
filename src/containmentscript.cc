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

#include "containmentscript.h"
#include <fst/script/script-impl.h>

namespace fst {
namespace script {

void Containment(const FstClass &ifst, const FstClass &sigma_star,
                 MutableFstClass *ofst) {
  if (!internal::ArcTypesMatch(ifst, sigma_star, "Containment") ||
      !internal::ArcTypesMatch(sigma_star, *ofst, "Containment")) {
    ofst->SetProperties(kError, kError);
    return;
  }
  ContainmentArgs args(ifst, sigma_star, ofst);
  Apply<Operation<ContainmentArgs>>("Containment", ifst.ArcType(), &args);
}

REGISTER_FST_OPERATION(Containment, StdArc, ContainmentArgs);
REGISTER_FST_OPERATION(Containment, LogArc, ContainmentArgs);
REGISTER_FST_OPERATION(Containment, Log64Arc, ContainmentArgs);

}  // namespace script
}  // namespace fst

