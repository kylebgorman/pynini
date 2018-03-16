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

#ifndef PYNINI_PYNINI_CDREWRITE_H_
#define PYNINI_PYNINI_CDREWRITE_H_

// This file contains two main utility functions which extend context-dependent
// rewrite rule compilation to better support symbol tables and boundary
// markers, in the style of Thrax. There are both arc-templated and
// template-free functions.

#include <fst/fstlib.h>
#include <fst/script/arg-packs.h>
#include <fst/script/fstscript.h>
#include "cdrewrite.h"
#include "sigma_star.h"
#include "pynini_common.h"

DECLARE_int32(left_boundary_index);
DECLARE_string(left_boundary_symbol);
DECLARE_int32(right_boundary_index);
DECLARE_string(right_boundary_symbol);
DECLARE_bool(cdrewrite_verify);

namespace fst {
namespace internal {

// Helpers for handling boundary symbols.

template <class Arc>
void AddBoundarySymbolArcsToSigmaStar(MutableFst<Arc> *sigma_star) {
  for (StateIterator<MutableFst<Arc>> siter(*sigma_star); !siter.Done();
       siter.Next()) {
    const auto state = siter.Value();
    if (sigma_star->Final(state) != Arc::Weight::Zero()) {
      sigma_star->AddArc(
          state, Arc(FLAGS_left_boundary_index, FLAGS_left_boundary_index,
                     Arc::Weight::One(), sigma_star->Start()));
      sigma_star->AddArc(
          state, Arc(FLAGS_right_boundary_index, FLAGS_right_boundary_index,
                     Arc::Weight::One(), sigma_star->Start()));
    }
  }
}

template <class Arc>
void MakeBoundaryInserter(const Fst<Arc> &sigma_star, MutableFst<Arc> *fst) {
  // The resulting FST inserts BOS superinitially and inserts EOS superfinally.
  VectorFst<Arc> tfst;
  auto start = tfst.AddState();
  auto end = tfst.AddState();
  tfst.SetStart(start);
  tfst.AddArc(start,
              Arc(0, FLAGS_left_boundary_index, Arc::Weight::One(), end));
  tfst.SetFinal(end, Arc::Weight::One());
  Concat(&tfst, sigma_star);
  start = fst->AddState();
  end = fst->AddState();
  fst->SetStart(start);
  fst->AddArc(start,
              Arc(0, FLAGS_right_boundary_index, Arc::Weight::One(), end));
  fst->SetFinal(end, Arc::Weight::One());
  Concat(tfst, fst);
}

// Helper for detecting unconditioned insertion rules.

template <class Arc>
bool AllInputEpsilons(const Fst<Arc> &fst) {
  for (StateIterator<Fst<Arc>> siter(fst); !siter.Done(); siter.Next()) {
    for (ArcIterator<Fst<Arc>> aiter(fst, siter.Value()); !aiter.Done();
         aiter.Next()) {
      if (aiter.Value().ilabel) return false;
    }
  }
  return true;
}

template <class Arc>
bool IsUnconditionedInsertion(const Fst<Arc> &tau, const Fst<Arc> &lambda,
                              const Fst<Arc> &rho) {
  // If any of the following are true, the requested rule is not an
  // unconditioned insertion:
  //
  // * tau has at least one arc without an epsilon input label
  // * rho has at least one arc without an epsilon label
  // * lambda has at least one arc without an epsilon label
  return (AllInputEpsilons(tau) && AllInputEpsilons(lambda) &&
          AllInputEpsilons(rho));
}

// The input FSTs are mutated during preparation. Outside of the internal
// namespace, the four input arguments are all immutable const references,
// and this is called after making mutable copies.

template <class Arc>
void PyniniCDRewrite(MutableFst<Arc> *tau, MutableFst<Arc> *lambda,
                     MutableFst<Arc> *rho, MutableFst<Arc> *sigma_star,
                     MutableFst<Arc> *ofst, CDRewriteDirection cd,
                     CDRewriteMode cm) {
  // Unconditioned insertion is not obviously well-defined, and breaks the
  // boundary symbol logic, so we forbid it explicitly here.
  if (IsUnconditionedInsertion(*tau, *lambda, *rho)) {
    FSTERROR() << "PyniniCDRewrite: Unconditioned insertion is undefined; "
               << "specify a non-null lambda or rho for any insertion rule";
    ofst->SetProperties(kError, kError);
    return;
  }
  VectorFst<Arc> inserter;
  MakeBoundaryInserter(*sigma_star, &inserter);
  // During compilation, all symbols are stored in a single "global" table,
  // while FST symbol tables are nulled out. The global table is initialized
  // from sigma_star's symbol table, as it is likely to be closer to the
  // "complete" table than other arguments. It does not contain the boundary
  // symbols, as these are deleted as a post-processing step. After compilation,
  // the global table is assigned to the output FST's input and output table.
  std::unique_ptr<SymbolTable> syms(sigma_star->InputSymbols()
                                        ? sigma_star->InputSymbols()->Copy()
                                        : nullptr);
  syms.reset(PrepareOutputSymbols(syms.get(), sigma_star));
  DeleteSymbols(sigma_star);
  // Gives a consistent labeling to boundary symbols in lambda and/or rho.
  if (syms) {
    syms->AddSymbol(FLAGS_left_boundary_symbol, FLAGS_left_boundary_index);
    syms->AddSymbol(FLAGS_right_boundary_symbol, FLAGS_right_boundary_index);
  }
  // Prepares remaining output.
  syms.reset(PrepareInputSymbols(syms.get(), tau));
  syms.reset(PrepareOutputSymbols(syms.get(), tau));
  DeleteSymbols(tau);
  syms.reset(PrepareInputSymbols(syms.get(), lambda));
  syms.reset(PrepareOutputSymbols(syms.get(), lambda));
  DeleteSymbols(lambda);
  syms.reset(PrepareInputSymbols(syms.get(), rho));
  syms.reset(PrepareOutputSymbols(syms.get(), rho));
  DeleteSymbols(rho);
  AddBoundarySymbolArcsToSigmaStar(sigma_star);
  // Actually compiles the rewrite rule.
  CDRewriteCompile(*tau, *lambda, *rho, *sigma_star, ofst, cd, cm);
  // Applies boundary filters.
  VectorFst<Arc> tfst;
  ArcSort(&inserter, OLabelCompare<Arc>());
  Compose(inserter, *ofst, &tfst);
  Invert(&inserter);  // `inserter` is now a deleter.
  ArcSort(&inserter, ILabelCompare<Arc>());
  Compose(tfst, inserter, ofst);
  // Reassigns symbol table to output.
  ofst->SetInputSymbols(syms.get());
  ofst->SetOutputSymbols(syms.get());
}

}  // namespace internal

// Makes copies of the input arguments then calls interval variant, which
// requires mutable input arguments.
template <class Arc>
void PyniniCDRewrite(const Fst<Arc> &tau, const Fst<Arc> &lambda,
                     const Fst<Arc> &rho, const Fst<Arc> &sigma_star,
                     MutableFst<Arc> *ofst, CDRewriteDirection cd,
                     CDRewriteMode cm) {
  VectorFst<Arc> tau_copy(tau);
  VectorFst<Arc> lambda_copy(lambda);
  VectorFst<Arc> rho_copy(rho);
  VectorFst<Arc> sigma_star_copy(sigma_star);
  internal::PyniniCDRewrite(&tau_copy, &lambda_copy, &rho_copy,
                            &sigma_star_copy, ofst, cd, cm);
}

// Scripting API wrapper of the above.

namespace script {

using PyniniCDRewriteArgs =
    std::tuple<const FstClass &, const FstClass &, const FstClass &,
               const FstClass &, MutableFstClass *, CDRewriteDirection,
               CDRewriteMode>;

template <class Arc>
void PyniniCDRewrite(PyniniCDRewriteArgs *args) {
  const Fst<Arc> &tau = *(std::get<0>(*args).GetFst<Arc>());
  const Fst<Arc> &lambda = *(std::get<1>(*args).GetFst<Arc>());
  const Fst<Arc> &rho = *(std::get<2>(*args).GetFst<Arc>());
  const Fst<Arc> &sigma_star_star = *(std::get<3>(*args).GetFst<Arc>());
  MutableFst<Arc> *ofst = std::get<4>(*args)->GetMutableFst<Arc>();
  PyniniCDRewrite(tau, lambda, rho, sigma_star_star, ofst, std::get<5>(*args),
                  std::get<6>(*args));
}

void PyniniCDRewrite(const FstClass &tau, const FstClass &lambda,
                     const FstClass &rho, const FstClass &sigma_star,
                     MutableFstClass *ofst, CDRewriteDirection cd,
                     CDRewriteMode cm);

}  // namespace script
}  // namespace fst

#endif  // PYNINI_PYNINI_CDREWRITE_H_

