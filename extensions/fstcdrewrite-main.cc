// Copyright 2016-2020 Google LLC
//
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


// Compiles a context-dependent rewrite rule.

#include <cstring>
#include <memory>
#include <string>

#include "base/commandlineflags.h"
#include "base/init_google.h"
#include "base/logging_extensions.h"
#include "cdrewritescript.h"
#include "getters.h"


DECLARE_string(direction);
DECLARE_string(mode);
DECLARE_int64(initial_boundary_marker);
DECLARE_int64(final_boundary_marker);

int fstcdrewrite_main(int argc, char **argv) {
  namespace s = nlp_fst::script;
  using nlp_fst::CDRewriteDirection;
  using nlp_fst::CDRewriteMode;
  using nlp_fst::script::FstClass;
  using nlp_fst::script::VectorFstClass;

  std::string usage = "Compiled context-dependent rewrite rule.\n\n  Usage: ";
  usage += argv[0];
  usage += " tau.fst lambda.fst rho.fst sigma.fst [out.fst]\n";

  InitGoogle(usage.c_str(), &argc, &argv, true);
  absl::SetFlag(&FLAGS_logtostderr, true);
  SetCommandLineOptionWithMode("minloglevel", "1", SET_FLAG_IF_DEFAULT);

  if (argc < 5 || argc > 6) {
    base::ReportCommandLineHelpMatch("fst");
    return 1;
  }

  const std::string tau_name = strcmp(argv[1], "-") != 0 ? argv[1] : "";
  const std::string lambda_name = strcmp(argv[2], "-") != 0 ? argv[2] : "";
  const std::string rho_name = strcmp(argv[3], "-") != 0 ? argv[3] : "";
  const std::string sigma_name = strcmp(argv[4], "-") != 0 ? argv[4] : "";
  const std::string out_name = strcmp(argv[5], "-") != 0 ? argv[5] : "";

  if (tau_name.empty() + lambda_name.empty() + rho_name.empty() +
          sigma_name.empty() >
      1) {
    LOG(ERROR) << argv[9]
               << ": Can't take more than one input from standard input";
    return 1;
  }

  const std::unique_ptr<const FstClass> tau(FstClass::Read(tau_name));
  if (!tau) return 1;

  const std::unique_ptr<const FstClass> lambda(FstClass::Read(lambda_name));
  if (!lambda) return 1;

  const std::unique_ptr<const FstClass> rho(FstClass::Read(rho_name));
  if (!rho) return 1;

  const std::unique_ptr<const FstClass> sigma(FstClass::Read(sigma_name));
  if (!sigma) return 1;

  CDRewriteDirection dir;
  if (!s::GetCDRewriteDirection(FLAGS_direction, &dir)) {
    LOG(ERROR) << argv[0] << ": Unknown or unsupported rewrite direction: "
               << FLAGS_direction;
    return 1;
  }

  CDRewriteMode mode;
  if (!s::GetCDRewriteMode(FLAGS_mode, &mode)) {
    LOG(ERROR) << argv[0]
               << ": Unknown or unsupported rewrite mode: " << FLAGS_mode;
    return 1;
  }

  VectorFstClass ofst(tau->ArcType());

  s::CDRewriteCompile(*tau, *lambda, *rho, *sigma, &ofst, dir, mode,
                      FLAGS_initial_boundary_marker,
                      FLAGS_final_boundary_marker);

  return !ofst.Write(out_name);
}

