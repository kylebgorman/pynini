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

#ifndef PYNINI_CROSSPRODUCT_H_
#define PYNINI_CROSSPRODUCT_H_

#include <fst/fstlib.h>
#include "optimize.h"

namespace fst {

// This function combines two acceptors into a cross-product transducer; that
// if U accepts V_U and L accepts V_L, then their cross-product U x L accepts
// \forall v_u \in V_U, v_l \in V_L: v_u \rightarrow v_r. If called with a
// transducer for the first argument (the upper language), it will act as if it
// had already been projected onto its input, and if called with a transducer
// for the second argument (the lower language), it will act as if it had
// already been projected onto its output.
template <class Arc>
void CrossProduct(
    const Fst<Arc> &ifst1, const Fst<Arc> &ifst2, MutableFst<Arc> *ofst,
    const typename Arc::Weight &final_weight = Arc::Weight::One()) {
  using Weight = typename Arc::Weight;
  // Initializes output FST using upper language.
  *ofst = ifst1;
  // Replaces output arcs on the upper language with epsilon, using the output
  // FST for temporary storage.
  OutputEpsilonMapper<Arc> oe_mapper;
  ArcMap(ofst, oe_mapper);
  // Replaces input arcs on the lower language with epsilon, using a temporary
  // mutable FST to store the mapped lower language.
  VectorFst<Arc> tfst(ifst2);
  InputEpsilonMapper<Arc> ie_mapper;
  ArcMap(&tfst, ie_mapper);
  // If a specific final weight is requested, apply it to all final states in
  // the lower language.
  if (final_weight != Weight::One()) {
    for (StateIterator<VectorFst<Arc>> siter(tfst); !siter.Done();
         siter.Next()) {
      const auto state = siter.Value();
      const auto &old_final_weight = tfst.Final(state);
      if (old_final_weight != Weight::Zero()) {
        tfst.SetFinal(state, Times(old_final_weight, final_weight));
      }
    }
  }
  // Concatenates the mapped lower language into the output FST.
  Concat(ofst, tfst);
  static constexpr auto props = kAcceptor | kString;
  // Optimizes output, if both inputs are string FSAs.
  if (ifst1.Properties(props, true) == props &&
      ifst2.Properties(props, true) == props) {
    OptimizeStringCrossProducts(ofst);
  }
  // Copies symbol tables (if present).
  ofst->SetInputSymbols(ifst1.InputSymbols());
  ofst->SetOutputSymbols(ifst2.OutputSymbols());
}

}  // namespace fst

#endif  // PYNINI_CROSSPRODUCT_H_

