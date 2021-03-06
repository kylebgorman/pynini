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

# Sanitize a dependency so that it works correctly from code that includes
# Pynini as a submodule.
def _clean_dep(dep):
    return str(Label(dep))

# Definite all external repositories required by Pynini.
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
    # because absl-py still supports Python 2.
    # -------------------------------------------------------------------------
    http_archive(
        name = "six_archive",
        build_file = _clean_dep("//bazel:six.BUILD.bazel"),
        sha256 = "70e8a77beed4562e7f14fe23a786b54f6296e34344c23bc42f07b15018ff98e9",
        strip_prefix = "six-1.11.0",
        urls = ["https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz#md5=d12789f9baf7e9fb#524c0c64f1773f8"],
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
        strip_prefix = "abseil-py-master",
        urls = ["https://github.com/abseil/abseil-py/archive/master.zip"],
    )

    # -------------------------------------------------------------------------
    # OpenFst: See
    #    http://www.openfst.org/twiki/pub/FST/FstDownload/README
    # -------------------------------------------------------------------------
    openfst_version = "1.8.1"

    http_archive(
        name = "org_openfst",
        urls = ["http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-%s.tar.gz"
                % openfst_version],
        sha256 = "24fb53b72bb687e3fa8ee96c72a31ff2920d99b980a0a8f61dda426fca6713f0",
        strip_prefix = "openfst-%s" % openfst_version,
    )

    # -------------------------------------------------------------------------
    # Cython:
    # -------------------------------------------------------------------------
    cython_version = "0.29.21"

    http_archive(
        name = "org_cython",
        build_file = _clean_dep("//bazel:cython.BUILD.bazel"),
        urls = ["https://github.com/cython/cython/archive/%s.tar.gz" % cython_version],
        sha256 = "e2e38e1f0572ca54d6085df3dec8b607d20e81515fb80215aed19c81e8fe2079",
        strip_prefix = "cython-%s" % cython_version,
    )
