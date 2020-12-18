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


// Creates the lenient composition of two FSTs w.r.t. some alphabet.

#include <cstring>
#include <memory>
#include <string>

#include "base/commandlineflags.h"
#include "base/init_google.h"
#include "base/logging_extensions.h"
#include "lenientlycomposescript.h"


int fstlenientlycompose_main(int argc, char **argv) {
  namespace s = nlp_fst::script;
  using nlp_fst::script::FstClass;
  using nlp_fst::script::VectorFstClass;

  std::string usage = "Creates the lenient composition of two FSTs w.r.t. ";
  usage += "some alphabet.\n\n  Usage: ";
  usage += argv[0];
  usage += " in1.fst in2.fst sigma.fst [out.fst]\n";

  InitGoogle(usage.c_str(), &argc, &argv, true);
  absl::SetFlag(&FLAGS_logtostderr, true);
  SetCommandLineOptionWithMode("minloglevel", "1", SET_FLAG_IF_DEFAULT);

  if (argc < 4 || argc > 5) {
    base::ReportCommandLineHelpMatch("fst");
    return 1;
  }

  const std::string in1_name = strcmp(argv[1], "-") != 0 ? argv[1] : "";
  const std::string in2_name = strcmp(argv[2], "-") != 0 ? argv[2] : "";
  const std::string ss_name = strcmp(argv[3], "-") != 0 ? argv[3] : "";
  const std::string out_name = argc > 4 ? argv[4] : "";

  if (in1_name.empty()) {
    if (in2_name.empty() || ss_name.empty()) {
      LOG(ERROR) << argv[0] << ": Can't take two inputs from standard input";
      return 1;
    }
  } else if (in2_name.empty() && ss_name.empty()) {
    LOG(ERROR) << argv[0] << ": Can't take two inputs from standard input";
    return 1;
  }

  const std::unique_ptr<const FstClass> ifst1(FstClass::Read(in1_name));
  if (!ifst1) return 1;

  const std::unique_ptr<const FstClass> ifst2(FstClass::Read(in2_name));
  if (!ifst2) return 1;

  const std::unique_ptr<const FstClass> sigma(FstClass::Read(ss_name));
  if (!sigma) return 1;

  VectorFstClass ofst(ifst1->ArcType());

  s::LenientlyCompose(*ifst1, *ifst2, *sigma, &ofst);

  return !ofst.Write(out_name);
}

