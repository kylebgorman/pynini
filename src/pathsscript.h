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

#ifndef PYNINI_PATHSSCRIPT_H_
#define PYNINI_PATHSSCRIPT_H_

#include <algorithm>
#include <vector>

#include <fst/string.h>
#include <fst/script/arg-packs.h>
#include <fst/script/fstscript.h>
#include "paths.h"

namespace fst {
namespace script {

// Helpers.

template <class Arc>
inline StringTokenType GetStringPrinterTokenType(StringTokenType type) {
  return static_cast<StringTokenType>(type);
}

// Virtual interface implemented by each concrete StatesImpl<F>.
class StringPathsImplBase {
 public:
  virtual bool Error() const = 0;
  virtual void IString(string *result) const = 0;
  virtual string IString() const = 0;
  virtual void OString(string *result) const = 0;
  virtual string OString() const = 0;
  virtual WeightClass Weight() const = 0;
  virtual void ILabels(std::vector<int64> *labels) const = 0;
  virtual std::vector<int64> ILabels() const = 0;
  virtual void OLabels(std::vector<int64> *labels) const = 0;
  virtual std::vector<int64> OLabels() const = 0;
  virtual bool Done() const = 0;
  virtual void Reset() = 0;
  virtual void Next() = 0;
  virtual ~StringPathsImplBase() {}
};

// Templated implementation.
template <class Arc>
class StringPathsImpl : public StringPathsImplBase {
 public:
  using Label = typename Arc::Label;

  StringPathsImpl(const Fst<Arc> &fst, StringTokenType itype,
                  StringTokenType otype, const SymbolTable *isyms = nullptr,
                  const SymbolTable *osyms = nullptr, bool rm_epsilon = true)
      : impl_(new StringPaths<Arc>(fst, itype, otype, isyms, osyms,
                                   rm_epsilon)) {}

  bool Error() const override { return impl_->Error(); }

  void IString(string *result) const override { impl_->IString(result); }

  string IString() const override { return impl_->IString(); }

  void OString(string *result) const override { impl_->OString(result); }

  string OString() const override { return impl_->OString(); }

  WeightClass Weight() const override { return WeightClass(impl_->Weight()); }

  void ILabels(std::vector<int64> *labels) const override {
    std::vector<Label> typed_labels;
    impl_->ILabels(&typed_labels);
    labels->clear();
    labels->resize(typed_labels.size());
    std::copy(typed_labels.begin(), typed_labels.end(), labels->begin());
  }

  std::vector<int64> ILabels() const override {
    std::vector<int64> labels;
    ILabels(&labels);
    return labels;
  }

  void OLabels(std::vector<int64> *labels) const override {
    std::vector<Label> typed_labels;
    impl_->OLabels(&typed_labels);
    labels->clear();
    labels->resize(typed_labels.size());
    std::copy(typed_labels.begin(), typed_labels.end(), labels->begin());
  }

  std::vector<int64> OLabels() const override {
    std::vector<int64> labels;
    OLabels(&labels);
    return labels;
  }

  void Reset() override { impl_->Reset(); }

  void Next() override { impl_->Next(); }

  bool Done() const override { return impl_->Done(); }

 private:
  std::unique_ptr<StringPaths<Arc>> impl_;
};

class StringPathsClass;

using InitStringPathsClassArgs =
    std::tuple<const FstClass &, StringTokenType, StringTokenType,
               const SymbolTable *, const SymbolTable *, bool,
               StringPathsClass *>;

// Untemplated user-facing class holding templated pimpl.
class StringPathsClass {
 public:
  StringPathsClass(const FstClass &fst, StringTokenType itype,
                   StringTokenType otype, const SymbolTable *isyms = nullptr,
                   const SymbolTable *osyms = nullptr, bool rm_epsilon = true);

  // Same as above, but applies the same string token type and symbol table
  // to both tapes.
  StringPathsClass(const FstClass &fst, StringTokenType type,
                   const SymbolTable *syms = nullptr, bool rm_epsilon = true)
      : StringPathsClass(fst, type, type, syms, syms, rm_epsilon) {}

  bool Error() const { return impl_->Error(); }

  void IString(string *result) const { impl_->IString(result); }

  string IString() const { return impl_->IString(); }

  void OString(string *result) const { impl_->OString(result); }

  string OString() const { return impl_->OString(); }

  WeightClass Weight() const { return WeightClass(impl_->Weight()); }

  void ILabels(std::vector<int64> *labels) const { impl_->ILabels(labels); }

  std::vector<int64> ILabels() const { return impl_->ILabels(); }

  void OLabels(std::vector<int64> *labels) const { impl_->OLabels(labels); }

  std::vector<int64> OLabels() const { return impl_->OLabels(); }

  void Reset() { impl_->Reset(); }

  void Next() { impl_->Next(); }

  bool Done() const { return impl_->Done(); }

  template <class Arc>
  friend void InitStringPathsClass(InitStringPathsClassArgs *args);

 private:
  std::unique_ptr<StringPathsImplBase> impl_;
};

template <class Arc>
void InitStringPathsClass(InitStringPathsClassArgs *args) {
  const Fst<Arc> &fst = *(std::get<0>(*args).GetFst<Arc>());
  std::get<6>(*args)->impl_.reset(new StringPathsImpl<Arc>(
      fst, std::get<1>(*args), std::get<2>(*args), std::get<3>(*args),
      std::get<4>(*args), std::get<5>(*args)));
}

}  // namespace script
}  // namespace fst

#endif  // PYNINI_PATHSSCRIPT_H_

