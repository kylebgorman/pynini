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
//
// Compiles context-dependent rewrite rules into weighted transducers.

#ifndef PYNINI_CDREWRITE_H_
#define PYNINI_CDREWRITE_H_

#include <memory>
#include <utility>
#include <vector>

#include <fst/types.h>
#include <fst/log.h>
#include <fst/compat.h>
#include <fst/fstlib.h>
#include "optimize.h"

namespace fst {

enum CDRewriteDirection { LEFT_TO_RIGHT, RIGHT_TO_LEFT, SIMULTANEOUS };
enum CDRewriteMode { OBLIGATORY, OPTIONAL };

namespace internal {

// This class is used to represent context-dependent rewrite rules.  A
// given rule can be compile into a weighted transducer using
// different parameters (direction, mode, alphabet) by calling
// Compile. See comments before constructor and Compile member
// function for detailed usage.
//
// For more information on the compilation procedure, see:
//
// Mohri, M., and Sproat, R. 1996. An efficient compiler for weighted rewrite
// rules. In Proc. ACL, 231-238.
template <class Arc>
class CDRewriteRule {
 public:
  using Label = typename Arc::Label;

  // Creates object representing the context-dependent rewrite rule:
  //
  //   phi -> psi / lamba __ rho .
  //
  // If phiXpsi is true, psi is a transducer with input domain phi instead of
  // an acceptor.
  //
  // phi, lambda, and rho must be unweighted acceptors and psi must be a
  // weighted transducer when phiXpsi is true and a weighted acceptor
  // otherwise.
  CDRewriteRule(const Fst<Arc> &phi, const Fst<Arc> &psi,
                const Fst<Arc> &lambda, const Fst<Arc> &rho, bool phiXpsi)
      : phi_(phi.Copy()),
        psi_(psi.Copy()),
        lambda_(lambda.Copy()),
        rho_(rho.Copy()),
        phiXpsi_(phiXpsi) {}

  // Builds the transducer representing the context-dependent rewrite rule.
  // sigma is an FST specifying (the closure of) the alphabet for the resulting
  // transducer. dir can be LEFT_TO_RIGHT, RIGHT_TO_LEFT or SIMULTANEOUS. mode
  // can be OBLIGATORY or OPTIONAL. sigma must be an unweighted acceptor
  // representing a bifix code.
  //
  // The error bit on the output FST is set if any argument does not satisfy the
  // preconditions.
  void Compile(const Fst<Arc> &sigma, MutableFst<Arc> *fst,
               CDRewriteDirection dir, CDRewriteMode mode);

 private:
  enum MarkerType { MARK = 1, CHECK = 2, CHECK_COMPLEMENT = 3};

  void MakeMarker(VectorFst<StdArc> *fst, const VectorFst<StdArc> &sigma,
                  MarkerType type,
                  const std::vector<std::pair<Label, Label> > &markers);

  void IgnoreMarkers(MutableFst<Arc> *fst,
                     const std::vector<std::pair<Label, Label> > &markers);

  void AddMarkersToSigma(MutableFst<Arc> *sigma,
                         const std::vector<std::pair<Label, Label> > &markers);

  void AppendMarkers(MutableFst<Arc> *fst,
                     const std::vector<std::pair<Label, Label> > &markers);

  void PrependMarkers(MutableFst<Arc> *fst,
                      const std::vector<std::pair<Label, Label> > &markers);

  void MakeFilter(const Fst<Arc> &beta,
                  const Fst<Arc> &sigma,
                  MutableFst<Arc> *filter,
                  MarkerType type,
                  const std::vector<std::pair<Label, Label> > &markers,
                  bool reverse);

  void MakeReplace(MutableFst<Arc> *fst, const Fst<Arc> &sigma);

  static Label MaxLabel(const Fst<Arc> &fst);

  std::unique_ptr<Fst<Arc>> phi_;
  std::unique_ptr<Fst<Arc>> psi_;
  std::unique_ptr<Fst<Arc>> lambda_;
  std::unique_ptr<Fst<Arc>> rho_;
  const bool phiXpsi_;
  CDRewriteDirection dir_;
  CDRewriteMode mode_;

  // The following labels are used to represent the symbols: <_1, <_2 and > in
  // Mohri and Sproat. For instance, for left-to-right obligatory rules, <_1 is
  // used to mark the start of an occurence of phi that need to be rewritten,
  // <_2 is used to mark the start of an occurence of phi that should not be
  // rewritten and > is used to mark the end of occurences of phi.
  Label lbrace1_;
  Label lbrace2_;
  Label rbrace_;

  CDRewriteRule(const CDRewriteRule &) = delete;
  CDRewriteRule &operator=(const CDRewriteRule &) = delete;
};

// Turns an FST into a marker transducer of specified type using the specified
// markers (markers) for the regular expression represented by the FST.
template <class Arc>
void CDRewriteRule<Arc>::MakeMarker(
    VectorFst<StdArc> *fst, const VectorFst<StdArc> &sigma, MarkerType type,
    const std::vector<std::pair<Label, Label>> &markers) {
  using StateId = StdArc::StateId;
  using Weight = StdArc::Weight;
  if (!(fst->Properties(kAcceptor, true) & kAcceptor)) {
    LOG(FATAL) << "Marker: input FST must be an acceptor";
  }
  auto num_states = fst->NumStates();
  // When num_states == 0, *fst is really Complement(sigma) and we build the
  // result upon sigma (== Complement(Complement(sigma))) directly in each case.
  switch (type) {
    case MARK:
      // Type 1: Insert (or delete) markers after each match.
      if (num_states == 0) {
        *fst = sigma;
      } else {
        for (StateId i = 0; i < num_states; ++i) {
          if (fst->Final(i) == Weight::Zero()) {
            fst->SetFinal(i, Weight::One());
          } else {
            const auto j = fst->AddState();
            fst->SetFinal(j, fst->Final(i));
            for (ArcIterator<StdFst> aiter(*fst, i); !aiter.Done();
                 aiter.Next()) {
              fst->AddArc(j, aiter.Value());
            }
            fst->SetFinal(i, Weight::Zero());
            fst->DeleteArcs(i);
            for (size_t k = 0; k < markers.size(); ++k) {
              fst->AddArc(i, StdArc(markers[k].first, markers[k].second,
                                    Weight::One(), j));
            }
          }
        }
      }
      break;
    case CHECK:
      // Type 2: Check that each marker is preceded by a match.
      if (num_states == 0) {
        *fst = sigma;
      } else {
        for (StateId i = 0; i < num_states; ++i) {
          if (fst->Final(i) == Weight::Zero()) {
            fst->SetFinal(i, Weight::One());
          } else {
            for (size_t k = 0; k < markers.size(); ++k) {
              fst->AddArc(i, StdArc(markers[k].first, markers[k].second,
                                    Weight::One(), i));
            }
          }
        }
      }
      break;
    case CHECK_COMPLEMENT:
      // Type 3: Check that each marker is not preceded by a match.
      if (num_states == 0) {
        *fst = sigma;
        num_states = fst->NumStates();
        for (StateId i = 0; i < num_states; ++i) {
          if (fst->Final(i) != Weight::Zero()) {
            for (size_t k = 0; k < markers.size(); ++k) {
              fst->AddArc(i, StdArc(markers[k].first, markers[k].second,
                                    Weight::One(), i));
            }
          }
        }
      } else {
        for (StateId i = 0; i < num_states; ++i) {
          if (fst->Final(i) == Weight::Zero()) {
            fst->SetFinal(i, Weight::One());
            for (size_t k = 0; k < markers.size(); ++k) {
              fst->AddArc(i, StdArc(markers[k].first, markers[k].second,
                                    Weight::One(), i));
            }
          }
        }
      }
      break;
  }
}

// Adds self loops allowing the markers at all states specified by markers in
// any position, corresponding to the subscripting conventions of Mohri &
// Sproat.
template <class Arc>
void CDRewriteRule<Arc>::IgnoreMarkers(
    MutableFst<Arc> *fst, const std::vector<std::pair<Label, Label>> &markers) {
  for (typename Arc::StateId i = 0; i < fst->NumStates(); ++i) {
    for (size_t k = 0; k < markers.size(); ++k) {
      fst->AddArc(i, Arc(markers[k].first, markers[k].second,
                         Arc::Weight::One(), i));
    }
  }
}

// Turns Sigma^* into (Sigma union markers)^*.
template <class Arc>
void CDRewriteRule<Arc>::AddMarkersToSigma(
    MutableFst<Arc> *sigma,
    const std::vector<std::pair<Label, Label>> &markers) {
  for (typename Arc::StateId s = 0; s < sigma->NumStates(); ++s) {
    if (sigma->Final(s) != Arc::Weight::Zero()) {
      for (size_t k = 0; k < markers.size(); ++k) {
        sigma->AddArc(s, Arc(markers[k].first, markers[k].second,
                             Arc::Weight::One(), sigma->Start()));
      }
    }
  }
}

// Adds loops at the initial state for all alphabet symbols in the current
// alphabet (sigma).
template <class Arc>
inline void PrependSigmaStar(MutableFst<Arc> *fst,
                             const Fst<Arc> &sigma) {
  Concat(sigma, fst);
  RmEpsilon(fst);
}

// Appends a transition for each of the (ilabel, olabel) pairs specified by the
// markers.
template <class Arc>
void CDRewriteRule<Arc>::AppendMarkers(
    MutableFst<Arc> *fst, const std::vector<std::pair<Label, Label>> &markers) {
  using Weight = typename Arc::Weight;
  VectorFst<Arc> temp_fst;
  const auto start_state = temp_fst.AddState();
  const auto final_state = temp_fst.AddState();
  temp_fst.SetStart(start_state);
  temp_fst.SetFinal(final_state, Weight::One());
  for (size_t k = 0; k < markers.size(); ++k) {
    temp_fst.AddArc(start_state, Arc(markers[k].first, markers[k].second,
                                     Weight::One(), final_state));
  }
  Concat(fst, temp_fst);
}

// Prepends a transition for each of the (ilabel, olabel) pairs specified by
// the markers.
template <class Arc>
void CDRewriteRule<Arc>::PrependMarkers(
    MutableFst<Arc> *fst, const std::vector<std::pair<Label, Label>> &markers) {
  if (fst->Start() == kNoStateId) fst->SetStart(fst->AddState());
  const auto new_start = fst->AddState();
  const auto old_start = fst->Start();
  fst->SetStart(new_start);
  for (size_t k = 0; k < markers.size(); ++k) {
    fst->AddArc(new_start, Arc(markers[k].first, markers[k].second,
                               Arc::Weight::One(), old_start));
  }
}

//
// Creates the marker transducer of the specified type for the markers defined
// in the markers argument for the regular expression sigma^* beta. When
// reverse is true, the reverse of the marker transducer corresponding to
// sigma^* reverse(beta).
//
// The operations in MakeFilter do not depend on the semiring, and indeed for
// some semirings the various optimizations needed in MakeFilter cause
// problems. We therefore map incoming acceptors in whatever semiring to
// unweighted acceptors. Ideally this would be in the boolean, but we simulate
// it with the tropical.
template <class Arc>
void CDRewriteRule<Arc>::MakeFilter(
    const Fst<Arc> &beta, const Fst<Arc> &sigma, MutableFst<Arc> *filter,
    MarkerType type, const std::vector<std::pair<Label, Label>> &markers,
    bool reverse) {
  VectorFst<StdArc> ufilter;
  Map(beta, &ufilter, RmWeightMapper<Arc, StdArc>());
  VectorFst<StdArc> usigma;
  Map(sigma, &usigma, RmWeightMapper<Arc, StdArc>());
  if (ufilter.Start() == kNoStateId) {
    ufilter.SetStart(ufilter.AddState());
  }
  if (reverse) {
    Reverse(MapFst<StdArc, StdArc, IdentityMapper<StdArc>>(
                ufilter, IdentityMapper<StdArc>()),
            &ufilter);
    VectorFst<StdArc> reversed_sigma;
    Reverse(usigma, &reversed_sigma);
    RmEpsilon(&reversed_sigma);
    PrependSigmaStar<StdArc>(&ufilter, reversed_sigma);
  } else {
    PrependSigmaStar<StdArc>(&ufilter, usigma);
  }
  RmEpsilon(&ufilter);
  DeterminizeFst<StdArc> det(ufilter);
  Map(det, &ufilter, IdentityMapper<StdArc>());
  Minimize(&ufilter);
  MakeMarker(&ufilter, usigma, type, markers);
  if (reverse) {
    Reverse(MapFst<StdArc, StdArc,
            IdentityMapper<StdArc> >(ufilter, IdentityMapper<StdArc>()),
            &ufilter);
  }
  ArcSort(&ufilter, ILabelCompare<StdArc>());
  Map(ufilter, filter, RmWeightMapper<StdArc, Arc>());
}

// Turns the FST representing phi X psi into a "replace" transducer.
template <class Arc>
void CDRewriteRule<Arc>::MakeReplace(MutableFst<Arc> *fst,
                                     const Fst<Arc> &sigma) {
  using StateId = typename Arc::StateId;
  using Weight = typename Arc::Weight;
  Optimize(fst);
  if (fst->Start() == kNoStateId) fst->SetStart(fst->AddState());
  // Label pairs for to be added arcs to the initial state or from the final
  // states.
  std::pair<Label, Label> initial_pair;
  std::pair<Label, Label> final_pair;
  // Label for self-loops to be added at the new initial state (to be created)
  // and at every other state.
  std::vector<std::pair<Label, Label>> initial_loops;
  std::vector<std::pair<Label, Label>> all_loops;
  switch (mode_) {
    case OBLIGATORY:
      all_loops.emplace_back(lbrace1_, 0);
      all_loops.emplace_back(lbrace2_, 0);
      all_loops.emplace_back(rbrace_, 0);
      switch (dir_) {
        case LEFT_TO_RIGHT:
          initial_pair = std::make_pair(lbrace1_, lbrace1_);
          final_pair = std::make_pair(rbrace_, 0);
          initial_loops.emplace_back(lbrace2_, lbrace2_);
          initial_loops.emplace_back(rbrace_, 0);
          break;
        case RIGHT_TO_LEFT:
          initial_pair = std::make_pair(rbrace_, 0);
          final_pair = std::make_pair(lbrace1_, lbrace1_);
          initial_loops.emplace_back(lbrace2_, lbrace2_);
          initial_loops.emplace_back(rbrace_, 0);
          break;
        case SIMULTANEOUS:
          initial_pair = std::make_pair(lbrace1_, 0);
          final_pair = std::make_pair(rbrace_, 0);
          initial_loops.emplace_back(lbrace2_, 0);
          initial_loops.emplace_back(rbrace_, 0);
          break;
      }
      break;
    case OPTIONAL:
      all_loops.emplace_back(rbrace_, 0);
      initial_loops.emplace_back(rbrace_, 0);
      switch (dir_) {
        case LEFT_TO_RIGHT:
          initial_pair = std::make_pair(0, lbrace1_);
          final_pair = std::make_pair(rbrace_, 0);
          break;
        case RIGHT_TO_LEFT:
          initial_pair = std::make_pair(rbrace_, 0);
          final_pair = std::make_pair(0, lbrace1_);
          break;
        case SIMULTANEOUS:
          initial_pair = std::make_pair(lbrace1_, 0);
          final_pair = std::make_pair(rbrace_, 0);
          break;
      }
      break;
  }
  // Adds loops at all states.
  IgnoreMarkers(fst, all_loops);
  // Creates new initial and final states.
  const auto num_states = fst->NumStates();
  const auto start_state = fst->AddState();
  const auto final_state = fst->AddState();
  fst->AddArc(start_state, Arc(initial_pair.first, initial_pair.second,
                               Weight::One(), fst->Start()));
  // Makes all final states non final with transition to new final state.
  for (StateId i = 0; i < num_states; ++i) {
    if (fst->Final(i) == Weight::Zero()) continue;
    fst->AddArc(i, Arc(final_pair.first, final_pair.second, fst->Final(i),
                       final_state));
    fst->SetFinal(i, Weight::Zero());
  }
  fst->SetFinal(final_state, Weight::One());
  fst->SetFinal(start_state, Weight::One());
  fst->SetStart(start_state);
  // Adds required loops at new initial state.
  VectorFst<Arc> sigma_m(sigma);
  AddMarkersToSigma(&sigma_m, initial_loops);
  PrependSigmaStar<Arc>(fst, sigma_m);
  Closure(fst, CLOSURE_STAR);
  Optimize(fst);
  ArcSort(fst, ILabelCompare<Arc>());
}

template <class Arc>
typename Arc::Label CDRewriteRule<Arc>::MaxLabel(const Fst<Arc> &fst) {
  Label max = kNoLabel;
  for (StateIterator<Fst<Arc>> siter(fst); !siter.Done(); siter.Next()) {
    for (ArcIterator<Fst<Arc>> aiter(fst, siter.Value()); !aiter.Done();
         aiter.Next()) {
      const auto &arc = aiter.Value();
      if (arc.ilabel > max) max = arc.ilabel;
      if (arc.olabel > max) max = arc.olabel;
    }
  }
  return max;
}

// Builds the transducer representing the context-dependent rewrite rule. sigma
// is an FST specifying (the closure of) the alphabet for the resulting
// transducer. dir can be LEFT_TO_RIGHT, RIGHT_TO_LEFT or SIMULTANEOUS. mode can
// be OBLIGATORY or OPTIONAL. sigma must be an unweighted acceptor representing
// a bifix code.
//
// The error bit on the output FST is set if any argument does not satisfy the
// preconditions.
template <class Arc>
void CDRewriteRule<Arc>::Compile(const Fst<Arc> &sigma, MutableFst<Arc> *fst,
                                 CDRewriteDirection dir, CDRewriteMode mode) {
  dir_ = dir;
  mode_ = mode;
  const auto props = kAcceptor | kUnweighted;
  if (phi_->Properties(props, true) != props) {
    FSTERROR() << "CDRewriteRule::Compile: phi must be an unweighted acceptor";
    fst->SetProperties(kError, kError);
    return;
  }
  if (lambda_->Properties(props, true) != props) {
    FSTERROR() << "CDRewriteRule::Compile: lambda must be an unweighted "
               << "acceptor";
    fst->SetProperties(kError, kError);
    return;
  }
  if (rho_->Properties(props, true) != props) {
    FSTERROR() << "CDRewriteRule::Compile: rho must be an unweighted acceptor";
    fst->SetProperties(kError, kError);
    return;
  }
  if (!phiXpsi_ && (psi_->Properties(kAcceptor, true) != kAcceptor)) {
    FSTERROR() << "CDRewriteRule::Compile: psi must be an acceptor or phiXpsi "
               << "must be set to true";
    fst->SetProperties(kError, kError);
    return;
  }
  if (sigma.Properties(props, true) != props) {
    FSTERROR() << "CDRewriteRule::Compile: sigma must be an unweighted "
               << "acceptor";
    fst->SetProperties(kError, kError);
    return;
  }
  rbrace_ = MaxLabel(sigma) + 1;
  lbrace1_ = rbrace_ + 1;
  lbrace2_ = rbrace_ + 2;
  VectorFst<Arc> sigma_rbrace(sigma);
  AddMarkersToSigma(&sigma_rbrace, {{rbrace_, rbrace_}});
  fst->DeleteStates();
  VectorFst<Arc> replace;
  if (phiXpsi_) {
    ArcMap(*psi_, &replace, IdentityMapper<Arc>());
  } else {
    Compose(ArcMapFst<Arc, Arc, OutputEpsilonMapper<Arc>>(
                *phi_, OutputEpsilonMapper<Arc>()),
            ArcMapFst<Arc, Arc, InputEpsilonMapper<Arc>>(
                *psi_, InputEpsilonMapper<Arc>()),
            &replace);
  }
  MakeReplace(&replace, sigma);
  switch (dir_) {
    case LEFT_TO_RIGHT: {
      // Builds r filter.
      VectorFst<Arc> r;
      MakeFilter(*rho_, sigma, &r, MARK, {{0, rbrace_}}, true);
      switch (mode_) {
        case OBLIGATORY: {
          VectorFst<Arc> phi_rbrace;  // Appends > after phi_, matches all >.
          Map(*phi_, &phi_rbrace, IdentityMapper<Arc>());
          IgnoreMarkers(&phi_rbrace, {{rbrace_, rbrace_}});
          AppendMarkers(&phi_rbrace, {{rbrace_, rbrace_}});
          // Builds f filter.
          VectorFst<Arc> f;
          MakeFilter(phi_rbrace, sigma_rbrace, &f, MARK,
                     {{0, lbrace1_}, {0, lbrace2_}}, true);
          // Builds l1 filter.
          VectorFst<Arc> l1;
          MakeFilter(*lambda_, sigma, &l1, CHECK, {{lbrace1_, 0}}, false);
          IgnoreMarkers(&l1, {{lbrace2_, lbrace2_}});
          ArcSort(&l1, ILabelCompare<Arc>());
          // Builds l2 filter.
          VectorFst<Arc> l2;
          MakeFilter(*lambda_, sigma, &l2, CHECK_COMPLEMENT, {{lbrace2_, 0}},
                     false);
          // Builds (((r o f) o replace) o l1) o l2.
          VectorFst<Arc> c;
          Compose(r, f, &c);
          Compose(c, replace, fst);
          Compose(*fst, l1, &c);
          Compose(c, l2, fst);
          break;
        }
        case OPTIONAL: {
          // Builds l filter.
          VectorFst<Arc> l;
          MakeFilter(*lambda_, sigma, &l, CHECK, {{lbrace1_, 0}}, false);
          // Builds (r o replace) o l.
          VectorFst<Arc> c;
          Compose(r, replace, &c);
          Compose(c, l, fst);
          break;
        }
      }
      break;
    }
    case RIGHT_TO_LEFT: {
      // Builds l filter.
      VectorFst<Arc> l;
      MakeFilter(*lambda_, sigma, &l, MARK, {{0, rbrace_}}, false);
      switch (mode_) {
        case OBLIGATORY: {
          VectorFst<Arc> rbrace_phi;  // Prepends > before phi, matches all >
          Map(*phi_, &rbrace_phi, IdentityMapper<Arc>());
          IgnoreMarkers(&rbrace_phi, {{rbrace_, rbrace_}});
          PrependMarkers(&rbrace_phi, {{rbrace_, rbrace_}});
          // Builds f filter.
          VectorFst<Arc> f;
          MakeFilter(rbrace_phi, sigma_rbrace, &f, MARK,
                     {{0, lbrace1_}, {0, lbrace2_}}, false);
          // Builds r1 filter.
          VectorFst<Arc> r1;
          MakeFilter(*rho_, sigma, &r1, CHECK, {{lbrace1_, 0}}, true);
          IgnoreMarkers(&r1, {{lbrace2_, lbrace2_}});
          ArcSort(&r1, ILabelCompare<Arc>());
          // Builds r2 filter.
          VectorFst<Arc> r2;
          MakeFilter(*rho_, sigma, &r2, CHECK_COMPLEMENT, {{lbrace2_, 0}},
                     true);
          // Builds (((l o f) o replace) o r1) o r2.
          VectorFst<Arc> c;
          Compose(l, f, &c);
          Compose(c, replace, fst);
          Compose(*fst, r1, &c);
          Compose(c, r2, fst);
          break;
        }
        case OPTIONAL: {
          // Builds r filter.
          VectorFst<Arc> r;
          MakeFilter(*rho_, sigma, &r, CHECK, {{lbrace1_, 0}}, true);
          // Builds (l o replace) o r.
          VectorFst<Arc> c;
          Compose(l, replace, &c);
          Compose(c, r, fst);
          break;
        }
      }
      break;
    }
    case SIMULTANEOUS: {
      // Builds r filter.
      VectorFst<Arc> r;
      MakeFilter(*rho_, sigma, &r, MARK, {{0, rbrace_}}, true);
      switch (mode_) {
        case OBLIGATORY: {
          VectorFst<Arc> phi_rbrace;  // Appends > after phi, matches all >.
          Map(*phi_, &phi_rbrace, IdentityMapper<Arc>());
          IgnoreMarkers(&phi_rbrace, {{rbrace_, rbrace_}});
          AppendMarkers(&phi_rbrace, {{rbrace_, rbrace_}});
          // Builds f filter.
          VectorFst<Arc> f;
          MakeFilter(phi_rbrace, sigma_rbrace, &f, MARK,
                     {{0, lbrace1_}, {0, lbrace2_}}, true);
          // Builds l1 filter.
          VectorFst<Arc> l1;
          MakeFilter(*lambda_, sigma, &l1, CHECK, {{lbrace1_, lbrace1_}},
                     false);
          IgnoreMarkers(&l1, {{lbrace2_, lbrace2_}, {rbrace_, rbrace_}});
          ArcSort(&l1, ILabelCompare<Arc>());
          // Builds l2 filter.
          VectorFst<Arc> l2;
          MakeFilter(*lambda_, sigma, &l2, CHECK_COMPLEMENT,
                     {{lbrace2_, lbrace2_}}, false);
          IgnoreMarkers(&l2, {{lbrace1_, lbrace1_}, {rbrace_, rbrace_}});
          ArcSort(&l2, ILabelCompare<Arc>());
          // Builds (((r o f) o l1) o l2) o replace.
          VectorFst<Arc> c;
          Compose(r, f, &c);
          Compose(c, l1, fst);
          Compose(*fst, l2, &c);
          Compose(c, replace, fst);
          break;
        }
        case OPTIONAL: {
          // Builds l filter.
          VectorFst<Arc> l;
          MakeFilter(*lambda_, sigma, &l, CHECK, {{0, lbrace1_}}, false);
          IgnoreMarkers(&l, {{rbrace_, rbrace_}});
          ArcSort(&l, ILabelCompare<Arc>());
          // Builds (r o l) o replace.
          VectorFst<Arc> c;
          Compose(r, l, &c);
          Compose(c, replace, fst);
          break;
        }
      }
      break;
    }
  }
  Optimize(fst);
  ArcSort(fst, ILabelCompare<Arc>());
}

}  // namespace internal.

// Builds a transducer representing the context-dependent rewrite rule:
//
//   phi -> psi / lamba __ rho .
//
// If phiXpsi is true, psi is a transducer with input domain phi instead of
// an acceptor.
//
// phi, lambda, and rho must be unweighted acceptors and psi must be a
// weighted transducer when phiXpsi is true and a weighted acceptor
// otherwise. sigma is an FST specifying (the closure of) the alphabet
// for the resulting transducer. dir can be LEFT_TO_RIGHT, RIGHT_TO_LEFT or
// SIMULTANEOUS. mode can be OBLIGATORY or OPTIONAL. sigma must be an unweighted
// acceptor representing a bifix code.
//
// The error bit on the output FST is set if any argument does not satisfy the
// preconditions.
template <class Arc>
void CDRewriteCompile(const Fst<Arc> &phi, const Fst<Arc> &psi,
                      const Fst<Arc> &lambda, const Fst<Arc> &rho,
                      const Fst<Arc> &sigma, MutableFst<Arc> *fst,
                      CDRewriteDirection dir, CDRewriteMode mode,
                      bool phiXpsi) {
  internal::CDRewriteRule<Arc> cdrule(phi, psi, lambda, rho, phiXpsi);
  cdrule.Compile(sigma, fst, dir, mode);
}

// Builds a transducer object representing the context-dependent rewrite rule:
//
//   phi -> psi / lamba __ rho .
//
// phi, lambda, and rho must be unweighted acceptors and psi must be a
// weighted acceptor. sigma is an FST specifying (the closure of) the alphabet
// for the resulting transducer. dir can be LEFT_TO_RIGHT, RIGHT_TO_LEFT or
// SIMULTANEOUS. mode can be OBLIGATORY or OPTIONAL. sigma must be an unweighted
// acceptor representing a bifix code.
//
// The error bit on the output FST is set if any argument does not satisfy the
// preconditions.
template <class Arc>
void CDRewriteCompile(const Fst<Arc> &phi, const Fst<Arc> &psi,
                      const Fst<Arc> &lambda, const Fst<Arc> &rho,
                      const Fst<Arc> &sigma, MutableFst<Arc> *fst,
                      CDRewriteDirection dir, CDRewriteMode mode) {
  CDRewriteCompile(phi, psi, lambda, rho, sigma, fst, dir, mode, false);
}

// Builds a transducer object representing the context-dependent rewrite rule:
//
//   phi -> psi / lamba __ rho .
//
// where tau represents the cross-product of phi X psi.
//
// Lambda, and rho must be unweighted acceptors. sigma is an FST specifying (the
// closure of) the alphabet for the resulting transducer. dir can be
// LEFT_TO_RIGHT, RIGHT_TO_LEFT or SIMULTANEOUS. mode can be OBLIGATORY or
// OPTIONAL. sigma must be an unweighted acceptor representing a bifix code.
//
// The error bit on the output FST is set if any argument does not satisfy the
// preconditions.
template <class Arc>
void CDRewriteCompile(const Fst<Arc> &tau, const Fst<Arc> &lambda,
                      const Fst<Arc> &rho, const Fst<Arc> &sigma,
                      MutableFst<Arc> *fst, CDRewriteDirection dir,
                      CDRewriteMode mode) {
  VectorFst<Arc> phi(tau);
  Project(&phi, PROJECT_INPUT);
  ArcMap(&phi, RmWeightMapper<Arc>());
  Optimize(&phi);
  CDRewriteCompile(phi, tau, lambda, rho, sigma, fst, dir, mode, true);
}

}  // namespace fst

#endif  // PYNINI_CD_REWRITE_H_

