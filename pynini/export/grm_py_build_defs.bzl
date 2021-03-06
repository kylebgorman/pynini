# Copyright 2016-2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Targets for compiling Pynini files into far files."""

load("@org_openfst//:src/extensions/far/build_defs.bzl", "convert_far_types")

def _compile_grm_py_bin_target(name, deps, data, is_multi_target):
    """Defines a target that builds the binary from a given Pynini file.

    Args:
      name: The name of the Pynini file (without extension).
      deps: The dependencies used in the Pynini file.
      is_multi_target: True, if the Pynini generates multiple outputs.
      data: Extra data dependencies used in the Pynini file.

    Returns:
      The name of the binary target.
    """
    if not deps:
        deps = []
    if not data:
        data = []

    template_prefix = "multi_" if is_multi_target else ""
    lib_name = "_" + name + "_lib"
    native.py_library(
        name = lib_name,
        srcs = [name + ".py"],
        deps = deps + [
            "@org_opengrm_pynini//pynini/export:%sgrm" % template_prefix,
        ],
        data = data,
        visibility = ["//visibility:private"],
        srcs_version = "PY3",
    )

    bin_name = "_" + name + "_bin"
    native.py_binary(
        name = bin_name,
        srcs = [name + ".py"],
        main = name + ".py",
        deps = [":" + lib_name],
        visibility = ["//visibility:private"],
        srcs_version = "PY3",
        python_version = "PY3",
    )
    return bin_name

def compile_grm_py(
        name,
        far_type = None,
        fst_type = None,
        deps = None,
        data = None,
        out = None,
        **kwds):
    """Provides a target to convert a Pynini file into a (portable) FAR file.

    Turns a Pynini file into a FAR file with the specified FAR and FST types.

    Args:
      name: The BUILD rule name and the file prefix for the generated output.
      far_type: An optional string specifying the FAR format.
      fst_type: An optional string specifying the format of the FSTs in the FAR
                archive.  The type must be supported by
                @org_openfst//:fst.
      deps: A list of other grammar targets that we'll need for this grammar.
      data: Extra data dependencies used in the Pynini file.
      out: Far file to be generated. If not present, then we'll use the `name`
           followed by ".far".
      **kwds: Attributes common to all BUILD rules, e.g., testonly, visibility.
    """
    out = out or (name + ".far")
    if not out.endswith(".far"):
        fail("Output filename \"{}\" must end with \".far\".".format(out))
    bin_name = _compile_grm_py_bin_target(name, deps, data, False)

    # Pynini produces far_type=sttable, fst_type=vector output by default.
    convert_far = far_type or (fst_type and fst_type != "vector")
    if convert_far:
        # If converting, we need temporary names for the genrule output, so
        # the conversion output can have the final name.
        genrule_out = name + ".farconvert.tmp"
        genrule_name = name + "_sttable"
    else:
        genrule_out = out
        genrule_name = name

    native.genrule(
        name = genrule_name,
        exec_tools = [bin_name],
        outs = [genrule_out],
        cmd = "$(location %s)" % bin_name + " --output \"$@\"",
        message = "Compiling Pynini file %s.py ==> %s in rule" % (name, genrule_out),
        **kwds
    )

    if convert_far:
        convert_far_types(
            name = name,
            far_in = genrule_out,
            far_out = out,
            far_type = far_type,
            fst_type = fst_type,
            **kwds
        )

def compile_multi_grm_py(
        name,
        outs,
        far_type = None,
        fst_type = None,
        deps = None,
        data = None,
        **kwds):
    """Provides a target to convert a Pynini file into multiple (portable) FAR files.

    Turns a Pynini file into a FAR file with the specified FAR and FST types.

    Args:
      name: The BUILD rule name and the file prefix for the generated output.
      outs: A dictionary mapping designators to files, where designator
            is the designating name used in the Pynini file to refer to the
            corresponding file. The designated files must have extension ".far".
      far_type: An optional string specifying the FAR format.
      fst_type: An optional string specifying the format of the FSTs in the FAR
                archives.  The type must be supported by
                @org_openfst//:fst.
      deps: A list of other compile_grm rules that we'll need for this grammar.
      data: Extra data dependencies used in the Pynini file.
      **kwds: Attributes common to all BUILD rules, e.g., testonly, visibility.
    """
    if not outs:
        fail("Must specify at least one mapping in `outs`.")
    bin_name = _compile_grm_py_bin_target(name, deps, data, True)

    # Pynini produces far_type=sttable, fst_type=vector output by default.
    convert_far = far_type or (fst_type and fst_type != "vector")

    genrule_outs_strings = []
    genrule_outs = []
    farmap_outs = [] if convert_far else None
    for target_name, file_name in outs.items():
        if not file_name.endswith(".far"):
            fail("Output filename \"{}\" must end with \".far\".".format(file_name))
        if convert_far:
            # If converting, we need temporary names for the genrule output,
            # so the conversion output can have the final name.
            genrule_out = file_name + ".farconvert.tmp"
            farmap_outs.append(file_name)
        else:
            genrule_out = file_name
        genrule_outs_strings.append("%s=$(location %s)" % (target_name, genrule_out))
        genrule_outs.append(genrule_out)

    # The last rule needs to have `name` as its name. The filegroup for the
    # sttable conversion always uses that since it can only be last.
    if convert_far:
        genrule_name = name + "_sttable"
        farmap_name = name
    else:
        genrule_name = name
        farmap_name = None

    native.genrule(
        name = genrule_name,
        exec_tools = [bin_name],
        outs = genrule_outs,
        cmd = ("$(location %s)" % bin_name +
               " --outputs " + ",".join(genrule_outs_strings)),
        message = "Compiling Pynini file %s.py into multiple FAR files in rule" % name,
        **kwds
    )

    # Target names from either fst or sttable conversion that need to be bundled
    # together to create the final filegroup called `name`.
    if convert_far:
        filegroup_names = []

        # Here we are relying on the guarantee that the iteration order of the dict is the
        # same as when we iterated above.
        # https://docs.bazel.build/versions/master/skylark/lib/dict.html#modules.dict
        for target_name, genrule_out, farmap_out in zip(outs.keys(), genrule_outs, farmap_outs):
            filegroup_name = farmap_name + "_" + target_name
            filegroup_names.append(filegroup_name)
            convert_far_types(
                name = filegroup_name,
                far_in = genrule_out,
                far_out = farmap_out,
                far_type = far_type,
                fst_type = fst_type,
                **kwds
            )
        native.filegroup(
            name = name,
            srcs = filegroup_names,
            **kwds
        )

