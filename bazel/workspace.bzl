# Copyright 2015-2020 Google LLC. All Rights Reserved.
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

"""Pynini external dependencies that can be loaded in a workspace file.

Please include this file in all the downstream Bazel dependencies of Pynini.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("//third_party/bazel:python_configure.bzl", "python_configure")

# Sanitizes a dependency so that it works correctly from code that includes
# Pynini as a submodule.
def _clean_dep(dep):
    return str(Label(dep))

# Defines all external repositories required by Pynini.
def pynini_repositories(name = ""):
    """All external dependencies for Pynini builds.

    Args:
      name: Name of the rule.
    """

    # -------------------------------------------------------------------------
    # Python extra Bazel rules for packaging: See
    #    https://github.com/bazelbuild/rules_python/tree/master
    # -------------------------------------------------------------------------
    http_archive(
        name = "rules_python",
        url = "https://github.com/bazelbuild/rules_python/releases/download/0.0.3/rules_python-0.0.3.tar.gz",
        sha256 = "e46612e9bb0dae8745de6a0643be69e8665a03f63163ac6610c210e80d14c3e4",
    )

    # -------------------------------------------------------------------------
    # Skylib is a standard library that provides functions useful for
    # manipulating collections, file paths, and other features that are useful
    # when writing custom build rules in Bazel. See:
    #    https://github.com/bazelbuild/bazel-skylib
    # -------------------------------------------------------------------------
    skylib_version = "1.0.3"

    http_archive(
        name = "bazel_skylib",
        url = "https://github.com/bazelbuild/bazel-skylib/releases/download/%s/bazel-skylib-%s.tar.gz" % (
            skylib_version,
            skylib_version,
        ),
        sha256 = "1c531376ac7e5a180e0237938a2536de0c54d93f5c278634818e0efc952dd56c",
    )

    # -------------------------------------------------------------------------
    # Python development headers.
    # -------------------------------------------------------------------------
    python_configure(name = "local_config_python")

    native.bind(
        name = "python_headers",
        actual = "@local_config_python//:python_headers",
    )

    # -------------------------------------------------------------------------
    # Six is a Python 2 and 3 compatibility library: It is still required
    # because absl-py still supports Python 2. See:
    #   https://github.com/benjaminp/six
    # -------------------------------------------------------------------------
    six_version = "1.16.0"

    http_archive(
        name = "six_archive",
        build_file = "@org_opengrm_pynini//bazel:six.BUILD.bazel",
        sha256 = "af6745f78dceb1ad5107dc6c2d3646c8cb57cf4668ba7b5427145a71a690f60e",
        strip_prefix = "six-%s" % six_version,
        urls = ["https://github.com/benjaminp/six/archive/refs/tags/%s.tar.gz" % six_version],
    )

    # -------------------------------------------------------------------------
    # Google Abseil - C++ and Python Common Libraries:
    # -------------------------------------------------------------------------
    http_archive(
        name = "com_google_absl",
        strip_prefix = "abseil-cpp-master",
        urls = ["https://github.com/abseil/abseil-cpp/archive/master.zip"],
    )
    http_archive(
        name = "io_abseil_py",
        strip_prefix = "abseil-py-main",
        urls = ["https://github.com/abseil/abseil-py/archive/main.zip"],
    )

    # -------------------------------------------------------------------------
    # OpenFst: See
    #    http://www.openfst.org/twiki/pub/FST/FstDownload/README
    # -------------------------------------------------------------------------
    openfst_version = "1.8.2"

    http_archive(
        name = "org_openfst",
        urls = ["https://www.openfst.org/twiki/pub/FST/FstDownload/openfst-%s.tar.gz" % openfst_version],
        sha256 = "de987bf3624721c5d5ba321af95751898e4f4bb41c8a36e2d64f0627656d8b42",
        strip_prefix = "openfst-%s" % openfst_version,
    )

    # -------------------------------------------------------------------------
    # Cython:
    # -------------------------------------------------------------------------
    cython_version = "0.29.24"

    http_archive(
        name = "org_cython",
        build_file = _clean_dep("//bazel:cython.BUILD.bazel"),
        urls = ["https://github.com/cython/cython/archive/%s.tar.gz" % cython_version],
        sha256 = "a5efb97612f0f97164e87c54cc295b2e2d06c539487670079963adeab872de80",
        strip_prefix = "cython-%s" % cython_version,
    )
