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
// Copyright 2016 and onwards Google, Inc.
//

// Creates the generalized closure of an FST.

#include <cstring>
#include <memory>
#include <string>

#include "base/commandlineflags.h"
#include "base/init_google.h"
#include "base/logging_extensions.h"
#include "concatrangescript.h"


DECLARE_int32(lower);
DECLARE_int32(upper);

int fstconcatrange_main(int argc, char **argv) {
  namespace s = nlp_fst::script;
  using nlp_fst::script::MutableFstClass;

  std::string usage = "Creates the generalized closure of an FST.\n\n  Usage: ";
  usage += argv[0];
  usage += " [in.fst [out.fst]]\n";

  InitGoogle(usage.c_str(), &argc, &argv, true);
  absl::SetFlag(&FLAGS_logtostderr, true);
  SetCommandLineOptionWithMode("minloglevel", "1", SET_FLAG_IF_DEFAULT);

  if (argc > 3) {
    ShowUsageWithFlagsRestrict(argv[0], "fst");
    return 1;
  }

  const std::string in_name =
      (argc > 1 && strcmp(argv[1], "-") != 0) ? argv[1] : "";
  const std::string out_name = argc > 2 ? argv[2] : "";

  const std::unique_ptr<MutableFstClass> fst(
      MutableFstClass::Read(in_name, true));
  if (!fst) return 1;

  s::ConcatRange(fst.get(), FLAGS_lower, FLAGS_upper);

  return !fst->Write(out_name);
}

