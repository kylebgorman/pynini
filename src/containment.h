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

#ifndef PYNINI_CONTAINMENT_H_
#define PYNINI_CONTAINMENT_H_

#include <fst/fstlib.h>
#include "sigma_star.h"

// FST containment, after:
//
// K. R. Beesley & L. Karttunen. 2003. Finite state morphology. Stanford, CA:
// CSLI. (p. 48f.)

namespace fst {

// The containment of a relation A is the union of all relations that contain
// some member of A as or as part of a larger concatenation. Here we compute
// containment with respect to sigma_star, a cyclic, unweighted acceptor
// representing the universal language. Then containment is simply:
//
// func Containment[A, sigma_star] {
//   return sigma_star A sigma_star;
// }

template <class Arc>
void Containment(const Fst<Arc> &ifst, const Fst<Arc> &sigma_star,
                 MutableFst<Arc> *ofst) {
  if (!internal::CheckSigmaStarProperties(sigma_star, "Containment")) {
    ofst->SetProperties(kError, kError);
    return;
  }
  *ofst = sigma_star;
  Concat(ofst, ifst);
  Concat(ofst, sigma_star);
}

}  // namespace fst

#endif  // PYNINI_CONTAINMENT_H_

