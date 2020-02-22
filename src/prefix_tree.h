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
#include <utility>

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

  struct ONode;  // Forward declaration.

  // Prefix tree node for the input labels of the FST.
  struct INode {
    std::map<Label, INode *> children;
    ONode *output;
    StateId state;

    INode() : output(nullptr), state(kNoStateId) {}
  };

  // Prefix tree node for the output labels of the FST.
  struct ONode {
    std::map<Label, ONode *> children;
    Weight weight;
    StateId state;

    ONode() : weight(Weight::Zero()), state(kNoStateId) {}
  };

  PrefixTree() : num_states_(0), root_(nullptr) {}

  ~PrefixTree() { Clear(); }

  StateId NumStates() const { return num_states_; }

  // Add an entry to the prefix tree, consisting of two label sequences and a
  // weight. Each label sequence must be provided as a pair of iterators.
  template <class Iterator1, class Iterator2, class T>
  void Add(Iterator1 it1, Iterator1 end1, Iterator2 it2, Iterator2 end2,
           T &&weight) {
    if (!root_) {
      CHECK_EQ(0, num_states_);
      root_ = new INode();
      root_->state = num_states_++;
    }
    INode *inode = root_;
    for (; it1 != end1; ++it1) {
      if (!*it1) continue;  // Skips over epsilons.
      inode = LookupOrInsertNew(&inode->children, *it1);
      if (kNoStateId == inode->state) inode->state = num_states_++;
    }
    if (!inode->output) {
      inode->output = new ONode();
      inode->output->state = num_states_++;
    }
    ONode *onode = inode->output;
    for (; it2 != end2; ++it2) {
      if (!*it2) continue;  // Skips over epsilons.
      onode = LookupOrInsertNew(&onode->children, *it2);
      if (kNoStateId == onode->state) onode->state = num_states_++;
    }
    onode->weight = Plus(onode->weight, std::forward<T>(weight));
  }

  // With semiring One as a default.
  template <class Iterator1, class Iterator2>
  void Add(Iterator1 it1, Iterator1 end1, Iterator2 it2, Iterator2 end2) {
    Add(it1, end1, it2, end2, Weight::One());
  }

  template <class Container1, class Container2, class T>
  void Add(const Container1 &cont1, const Container2 &cont2, T &&weight) {
    Add(cont1.begin(), cont1.end(), cont2.begin(), cont2.end(),
        std::forward<T>(weight));
  }

  // With semiring One as a default.
  template <class Container1, class Container2>
  void Add(const Container1 &cont1, const Container2 &cont2) {
    Add(cont1.begin(), cont1.end(), cont2.begin(), cont2.end(), Weight::One());
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
      INode *inode = iq.top();
      iq.pop();
      // Found a root node of an output trie.
      if (inode->output) oq.push(inode->output);
      for (const auto &item : inode->children) {
        iq.push(item.second);
      }
      delete inode;
    }
    // Second, perform simple depth-first traversals over the output tries,
    // starting at their root nodes.
    while (!oq.empty()) {
      ONode *onode = oq.top();
      oq.pop();
      for (const auto &item : onode->children) {
        oq.push(item.second);
      }
      delete onode;
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
    fst->AddStates(num_states_);
    fst->SetStart(root_->state);
    std::stack<INode *> iq;
    std::stack<ONode *> oq;
    iq.push(root_);
    while (!iq.empty()) {
      INode *inode = iq.top();
      iq.pop();
      const auto q = inode->state;
      CHECK_NE(kNoStateId, q);
      ONode *onode = inode->output;
      fst->ReserveArcs(q, (onode ? 1 : 0) + inode->children.size());
      if (onode) {
        fst->AddArc(q, Arc(0, 0, onode->state));
        oq.push(onode);
      }
      for (const auto &item : inode->children) {
        fst->AddArc(q, Arc(item.first, 0, item.second->state));
        iq.push(item.second);
      }
    }
    while (!oq.empty()) {
      ONode *onode = oq.top();
      oq.pop();
      const auto q = onode->state;
      CHECK_NE(kNoStateId, q);
      for (const auto &item : onode->children) {
        fst->AddArc(q, Arc(0, item.first, item.second->state));
        oq.push(item.second);
      }
      fst->SetFinal(q, onode->weight);
    }
  }

 private:
  StateId num_states_;
  INode *root_;

  PrefixTree(const PrefixTree &) = delete;
  PrefixTree &operator=(const PrefixTree &) = delete;
};

}  // namespace fst

#endif  // PYNINI_PREFIX_TREE_H_

