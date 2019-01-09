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
namespace internal {

// Marks the start state final.
template <class Arc>
void SetStartFinal(MutableFst<Arc> *fst) {
  fst->SetFinal(fst->Start(), Arc::Weight::One());
}

// Marks the start state final and then concatenates a copy, repeatedly.
template <class Arc>
void SetStartFinalAndConcat(const MutableFst<Arc> &copy, MutableFst<Arc> *fst,
                            int32 count) {
  for (; count > 0; --count) {
    SetStartFinal(fst);
    Concat(copy, fst);
  }
}

// Concatenates, repeatedly.
template <class Arc>
void Concat(const MutableFst<Arc> &copy, MutableFst<Arc> *fst, int32 count) {
  for (; count > 0; --count) Concat(copy, fst);
}

}  // namespace internal

// This function is a generalization of FST closure and PCRE's curly brace
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
// quantifier in PCRE. And, Repeat(A, 2, 5) mutates A so that it behaves like
// the concatenation of between 2 and 5 A's.
//
// When the third argument is zero, it is interpreted to indicate an infinite
// upper bound. Thus, Repeat(A, 1, 0) is equivalent to Closure(A, CLOSURE_PLUS).
//
// The following provide equvialents to the PCRE operators:
//
//     /x*/        Repeat(x, 0, 0)
//     /x+/        Repeat(x, 1, 0)
//     /x?/        Repeat(x, 0, 1)
//     /x{N}/      Repeat(x, N, N)
//     /x{M,N}/    Repeat(x, M, N)
//     /x{N,}/     Repeat(x, N, 0)
//     /x{,N}/     Repeat(x, 0, N)
template <class Arc>
void Repeat(MutableFst<Arc> *fst, int32 lower = 0, int32 upper = 0) {
  if (fst->Start() == kNoStateId) return;
  const std::unique_ptr<const MutableFst<Arc>> copy(fst->Copy());
  if (upper == 0) {
    // Infinite upper bound.
    // The last element in the concatenation is star-closed; remaining
    // concatenations are copies of the input.
    Closure(fst, CLOSURE_STAR);
    internal::Concat(*copy, fst, lower);
  } else if (lower == 0) {
    // Finite upper bound, lower bound includes zero.
    internal::SetStartFinal(fst);
    internal::SetStartFinalAndConcat(*copy, fst, upper - 1);
    internal::SetStartFinal(fst);
  } else {
    // Finite upper bound, lower bound does not include zero.
    internal::SetStartFinalAndConcat(*copy, fst, upper - lower);
    internal::Concat(*copy, fst, lower - 1);
  }
}

}  // namespace fst

#endif  // PYNINI_REPEAT_H_

