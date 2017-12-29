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

#include "pynini_replace.h"

namespace fst {
namespace script {

void PyniniReplace(const FstClass &root,
                   const std::vector<StringFstClassPair> &pairs,
                   MutableFstClass *ofst, const ReplaceOptions &opts) {
  if (!internal::ArcTypesMatch(root, *ofst, "PyniniReplace")) {
    ofst->SetProperties(kError, kError);
    return;
  }
  for (auto it = pairs.cbegin(); it != pairs.cend(); ++it) {
    if (!internal::ArcTypesMatch(*it->second, *ofst, "PyniniReplace")) {
      ofst->SetProperties(kError, kError);
      return;
    }
  }
  PyniniReplaceArgs args(root, pairs, ofst, opts);
  Apply<Operation<PyniniReplaceArgs>>("PyniniReplace", ofst->ArcType(), &args);
}

REGISTER_FST_OPERATION(PyniniReplace, StdArc, PyniniReplaceArgs);
REGISTER_FST_OPERATION(PyniniReplace, LogArc, PyniniReplaceArgs);
REGISTER_FST_OPERATION(PyniniReplace, Log64Arc, PyniniReplaceArgs);

void PyniniPdtReplace(const FstClass &root,
                      const std::vector<StringFstClassPair> &pairs,
                      MutableFstClass *ofst, std::vector<LabelPair> *parens,
                      PdtParserType type) {
  if (!internal::ArcTypesMatch(root, *ofst, "PyniniReplace")) {
    ofst->SetProperties(kError, kError);
    return;
  }
  for (auto it = pairs.cbegin(); it != pairs.cend(); ++it) {
    if (!internal::ArcTypesMatch(*it->second, *ofst, "PyniniPdtReplace")) {
      ofst->SetProperties(kError, kError);
      return;
    }
  }
  PyniniPdtReplaceArgs args(root, pairs, ofst, parens, type);
  Apply<Operation<PyniniPdtReplaceArgs>>("PyniniPdtReplace", ofst->ArcType(),
                                         &args);
}

REGISTER_FST_OPERATION(PyniniPdtReplace, StdArc, PyniniPdtReplaceArgs);
REGISTER_FST_OPERATION(PyniniPdtReplace, LogArc, PyniniPdtReplaceArgs);
REGISTER_FST_OPERATION(PyniniPdtReplace, Log64Arc, PyniniPdtReplaceArgs);

}  // namespace script
}  // namespace fst

