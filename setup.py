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

from Cython.Build import cythonize
from setuptools import Extension, setup


COMPILE_ARGS = [
    "-std=c++17",
    "-Wno-register",
    "-Wno-unused-function",
    "-Wno-unused-local-typedefs",
    "-funsigned-char",
]

LIBRARIES = ["fstfarscript", "fstfar", "fstscript", "fst", "m", "dl"]

pywrapfst = Extension(
    name="pywrapfst",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    libraries=LIBRARIES,
    sources=["src/pywrapfst.pyx"],
)

pynini = Extension(
    name="pynini",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    libraries=["fstmpdtscript", "fstpdtscript"] + LIBRARIES,
    sources=[
        "src/pynini.pyx",
        "src/cdrewritescript.cc",
        "src/concatrangescript.cc",
        "src/crossproductscript.cc",
        "src/getters.cc",
        "src/gtl.cc",
        "src/lenientlycomposescript.cc",
        "src/optimizescript.cc",
        "src/pathsscript.cc",
        "src/stringcompile.cc",
        "src/stringcompilescript.cc",
        "src/stringfile.cc",
        "src/stringmapscript.cc",
        "src/stringprintscript.cc",
        "src/stripcomment.cc",
    ],
)

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf8") as source:
  long_description = source.read()

__version__ = "2.1.0"

setup(
    name="pynini",
    version=__version__,
    author="Kyle Gorman",
    author_email="kbg@google.com",
    description="Finite-state grammar compilation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://pynini.opengrm.org",
    keywords=[
        "natural language processing",
        "speech recognition",
        "machine learning",
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    license="Apache 2.0",
    zip_safe=False,
    install_requires=["Cython >= 0.29"],
    ext_modules=cythonize([pywrapfst, pynini]),
)
