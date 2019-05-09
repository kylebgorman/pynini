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
# Copyright 2016 and onwards Google, Inc.
#
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.


from io import open
from os import path
from setuptools import Extension, setup

COMPILE_ARGS = ["-std=c++11",
                "-Wno-unused-function",
                "-Wno-unused-local-typedefs",
                "-funsigned-char"]

pywrapfst = Extension(name="pywrapfst", language="c++",
                      extra_compile_args=COMPILE_ARGS,
                      libraries=["fstfarscript", "fstfar", "fstscript",
                                 "fst", "m", "dl"],
                      sources=["src/pywrapfst.cc"])

pynini = Extension(
    name="pynini",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    libraries=[
        "fstfarscript", "fstpdtscript", "fstmpdtscript", "fstscript", "fstfar",
        "fst", "m", "dl"
    ],
    sources=[
        "src/stringtokentype.cc", "src/stringprintscript.cc",
        "src/stringmapscript.cc", "src/stringfile.cc",
        "src/stringcompilescript.cc", "src/stringcompile.cc",
        "src/repeatscript.cc", "src/pynini_replace.cc",
        "src/pynini_cdrewrite.cc", "src/pynini.cc", "src/pathsscript.cc",
        "src/optimizescript.cc", "src/mergesymbolsscript.cc",
        "src/mergesymbols.cc", "src/lenientlycomposescript.cc", "src/gtl.cc",
        "src/getters.cc", "src/crossproductscript.cc"
    ])

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf8") as source:
  long_description = source.read()

setup(
    name="pynini",
    version="2.0.7",
    description="Finite-state grammar compilation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kyle Gorman",
    author_email="kbg@google.com",
    url="http://pynini.opengrm.org",
    keywords=[
        "natural language processing", "speech recognition", "machine learning"
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment", "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    ext_modules=[pywrapfst, pynini],
    test_suite="pynini_test")
