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

#include "pynini_cdrewrite.h"

DEFINE_int32(left_boundary_index, 0x10fffc,
             "Index for the beginning-of-string symbol");
DEFINE_string(left_boundary_symbol, "BOS", "Beginning-of-string symbol");
DEFINE_int32(right_boundary_index, 0x10fffd,
             "Index for the end-of-string symbol");
DEFINE_string(right_boundary_symbol, "EOS", "End-of-string symbol");

namespace fst {
namespace script {

void PyniniCDRewrite(const FstClass &tau, const FstClass &lambda,
                     const FstClass &rho, const FstClass &sigma_star,
                     MutableFstClass *fst, CDRewriteDirection cd,
                     CDRewriteMode cm) {
  if (!internal::ArcTypesMatch(tau, lambda, "PyniniCDRewrite") ||
      !internal::ArcTypesMatch(lambda, rho, "PyniniCDRewrite") ||
      !internal::ArcTypesMatch(rho, sigma_star, "PyniniCDRewrite"))
    return;
  PyniniCDRewriteArgs args(tau, lambda, rho, sigma_star, fst, cd, cm);
  Apply<Operation<PyniniCDRewriteArgs>>("PyniniCDRewrite", fst->ArcType(),
                                        &args);
}

REGISTER_FST_OPERATION(PyniniCDRewrite, StdArc, PyniniCDRewriteArgs);
REGISTER_FST_OPERATION(PyniniCDRewrite, LogArc, PyniniCDRewriteArgs);
REGISTER_FST_OPERATION(PyniniCDRewrite, Log64Arc, PyniniCDRewriteArgs);

}  // namespace script
}  // namespace fst

