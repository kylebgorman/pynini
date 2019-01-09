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

#ifndef PYNINI_PREFIX_TREE_H_
#define PYNINI_PREFIX_TREE_H_

#include <map>
#include <stack>

#include <fst/compat.h>
#include <fst/log.h>
#include <fst/arc.h>
#include <fst/vector-fst.h>
#include "gtl.h"

namespace fst {

// This class is neither thread-safe nor thread-hostile.
template <class Arc>
class PrefixTree {
 public:
  using Label = typename Arc::Label;
  using StateId = typename Arc::StateId;
  using Weight = typename Arc::Weight;

  struct INode;
  struct ONode;

  using ichild_map = std::map<Label, INode *>;
  using ochild_map = std::map<Label, ONode *>;

  // Prefix tree node for the input labels of the FST.
  struct INode {
    ichild_map children;
    ONode *output;
    StateId state;

    INode() : output(nullptr), state(kNoStateId) {}
  };

  // Prefix tree node for the output labels of the FST.
  struct ONode {
    ochild_map children;
    Weight weight;
    StateId state;

    ONode() : weight(Weight::Zero()), state(kNoStateId) {}
  };

  PrefixTree() : num_states_(0), root_(nullptr) {}

  PrefixTree(const PrefixTree &) = delete;

  PrefixTree &operator=(const PrefixTree &) = delete;

  ~PrefixTree() { Clear(); }

  StateId NumStates() const { return num_states_; }

  // Add an entry to the prefix tree, consisting of two label sequences and a
  // weight. Each label sequence must be provided as a pair of iterators.
  template <class Iterator1, class Iterator2>
  void Add(Iterator1 iter1, Iterator1 end1,
           Iterator2 iter2, Iterator2 end2,
           const Weight &weight = Weight::One()) {
    if (!root_) {
      CHECK_EQ(0, num_states_);
      root_ = new INode();
      root_->state = num_states_++;
    }
    INode *n = root_;
    for (; iter1 != end1; ++iter1) {
      if (!*iter1) continue;  // Skips over epsilons.
      n = LookupOrInsertNew(&n->children, *iter1);
      if (kNoStateId == n->state) n->state = num_states_++;
    }
    if (!n->output) {
      n->output = new ONode();
      n->output->state = num_states_++;
    }
    ONode *o = n->output;
    for (; iter2 != end2; ++iter2) {
      if (!*iter2) continue;  // Skips over epsilons.
      o = LookupOrInsertNew(&o->children, *iter2);
      if (kNoStateId == o->state) o->state = num_states_++;
    }
    o->weight = Plus(o->weight, weight);
  }

  template <class Container1, class Container2>
  void Add(const Container1 &cont1, const Container2 &cont2,
           const Weight &weight = Weight::One()) {
    Add(cont1.begin(), cont1.end(), cont2.begin(), cont2.end(), weight);
  }

  // Removes all elements from this prefix tree.
  void Clear() {
    if (!root_) {
      CHECK_EQ(0, num_states_);
      return;
    }
    std::stack<INode *> iq;
    std::stack<ONode *> oq;
    // First, performs a simple depth-first traversal over the input trie,
    // starting at the root node. Node coloring is not needed, since we're
    // dealing with a tree.
    iq.push(root_);
    while (!iq.empty()) {
      INode *n = iq.top();
      iq.pop();
      if (n->output)
        oq.push(n->output);  // Found a root node of an output trie.
      for (auto iter = n->children.begin(); iter != n->children.end(); ++iter) {
        iq.push(iter->second);
      }
      delete n;
    }
    // Second, perform simple depth-first traversals over the output tries,
    // starting at their root nodes.
    while (!oq.empty()) {
      ONode *o = oq.top();
      oq.pop();
      for (auto oter = o->children.begin(); oter != o->children.end(); ++oter) {
        oq.push(oter->second);
      }
      delete o;
    }
    num_states_ = 0;
    root_ = nullptr;
  }

  // Write the current prefix tree transducer to a mutable FST.
  void ToFst(MutableFst<Arc> *fst) const {
    fst->DeleteStates();
    if (num_states_ == 0) {
      CHECK(!root_);
      return;
    }
    // For the creation of the FST to be efficient, we reserve enough space
    // for the states and arcs to avoid reallocation and internal copying.
    fst->ReserveStates(num_states_);
    for (StateId i = 0; i < num_states_; ++i) fst->AddState();
    fst->SetStart(root_->state);
    std::stack<INode *> iq;
    std::stack<ONode *> oq;
    iq.push(root_);
    while (!iq.empty()) {
      INode *n = iq.top();
      iq.pop();
      const auto q = n->state;
      CHECK_NE(kNoStateId, q);
      ONode *o = n->output;
      fst->ReserveArcs(q, (o ? 1 : 0) + n->children.size());
      if (o) {
        fst->AddArc(q, Arc(0, 0, Arc::Weight::One(), o->state));
        oq.push(o);
      }
      for (auto iter = n->children.begin(); iter != n->children.end(); ++iter) {
        fst->AddArc(q, Arc(iter->first, 0, Arc::Weight::One(),
                           iter->second->state));
        iq.push(iter->second);
      }
    }
    while (!oq.empty()) {
      ONode *o = oq.top();
      oq.pop();
      StateId q = o->state;
      CHECK_NE(kNoStateId, q);
      for (auto oter = o->children.begin(); oter != o->children.end(); ++oter) {
        fst->AddArc(q, Arc(0, oter->first, Arc::Weight::One(),
                           oter->second->state));
        oq.push(oter->second);
      }
      fst->SetFinal(q, o->weight);
    }
  }

 private:
  StateId num_states_;
  INode *root_;
};

}  // namespace fst

#endif  // PYNINI_PREFIX_TREE_H_

