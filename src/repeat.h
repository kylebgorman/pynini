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

#ifndef PYNINI_REPEAT_H_
#define PYNINI_REPEAT_H_

#include <memory>

#include <fst/types.h>
#include <fst/fstlib.h>

namespace fst {

// This function is a generalization of FST closure and Perl's curly brace
// quantifiers. It destructively computes the concatenative closure of an input
// FST as follows. If A transduces strings x to y with weight w, then
// Repeat(A, 0, 0) is equivalent to Closure(A, CLOSURE_STAR) which mutates A so
// that it transduces between empty strings with weight One, transduces strings
// x to y with weight w, transduces xx to yy with weight w \otimes w, strings
// xxx to yyy with weight w \otimes w \otimes w (and so on).
//
// When called with two non-zero positive integers as the trailing arguments,
// these act as upper and lower bounds, respectively, for the number of cycles
// through the original FST one is permitted to take in the modified FST. So,
// Repeat(A, 0, 1) is mutates A so it transduces between empty strings with
// weight One and // transduces strings x to y with weight w, similar to the ?
// quantifier in Perl. And, Repeat(A, 2, 5) mutates A so that it behaves like
// the concatenation of between 2 and 5 A's.
//
// When the third argument is zero, it is interpreted to indicate an infinite
// upper bound. Thus, Repeat(A, 1, 0) is equivalent to Closure(A, CLOSURE_PLUS).
//
// The following provide equvialents to the Perl operators:
//
//     /x*/        Repeat(x, 0, 0)
//     /x+/        Repeat(x, 1, 0)
//     /x?/        Repeat(x, 0, 1)
//     /x{N}/      Repeat(x, N, N)
//     /x{M,N}/    Repeat(x, M, N)
//     /x{N,}/     Repeat(x, N, 0)
//     /x{,N}/     Repeat(x, 0, N)

template <class Arc>
void Repeat(MutableFst<Arc> *fst, int32 lower, int32 upper) {
  using Weight = typename Arc::Weight;
  // Special cases.
  // Empty FST.
  if (fst->Start() == kNoStateId) return;
  // Star- or plus-closures.
  if (upper <= 0) {
    if (lower <= 0) {
      Closure(fst, CLOSURE_STAR);
      return;
    } else if (lower == 1) {
      Closure(fst, CLOSURE_PLUS);
      return;
    }
  }
  // Generic cases.
  // Lower bound includes 0.
  if (lower <= 0) {
    fst->SetFinal(fst->Start(), Weight::One());
  }
  std::unique_ptr<MutableFst<Arc>> tfst(fst->Copy());
  for (int32 i = 0; i < lower - 1; ++i) Concat(fst, *tfst);
  if (upper <= 0) {  // Upper bound is infinite.
    // Concatenates a *-ed copy.
    Closure(tfst.get(), CLOSURE_STAR);
    Concat(fst, *tfst);
  } else {  // Upper bound is finite.
    // Concatenates ?-ed copies.
    tfst->SetFinal(tfst->Start(), Weight::One());
    for (int32 i = lower; i < upper; ++i) Concat(fst, *tfst);
  }
}

}  // namespace fst

#endif  // PYNINI_REPEAT_H_

