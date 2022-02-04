# Copyright 2016-2021 Google LLC
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
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.

import os.path
import pathlib
import sys

from Cython.Build import cythonize
from setuptools import Extension
from setuptools import find_packages
from setuptools import setup


COMPILE_ARGS = [
    "-std=c++17",
    "-Wno-register",
    "-Wno-deprecated-declarations",
    "-Wno-unused-function",
    "-Wno-unused-local-typedefs",
    "-funsigned-char",
]
if sys.platform.startswith("darwin"):
  COMPILE_ARGS.append("-stdlib=libc++")
  COMPILE_ARGS.append("-mmacosx-version-min=10.7")


LIBRARIES = ["fstfarscript", "fstfar", "fstscript", "fst", "m", "dl"]


pywrapfst = Extension(
    name="_pywrapfst",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    libraries=LIBRARIES,
    sources=["extensions/_pywrapfst.pyx"],
)
pynini = Extension(
    name="_pynini",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    libraries=["fstmpdtscript", "fstpdtscript"] + LIBRARIES,
    sources=[
        "extensions/_pynini.pyx",
        "extensions/cdrewritescript.cc",
        "extensions/concatrangescript.cc",
        "extensions/crossscript.cc",
        "extensions/defaults.cc",
        "extensions/getters.cc",
        "extensions/lenientlycomposescript.cc",
        "extensions/optimizescript.cc",
        "extensions/pathsscript.cc",
        "extensions/stringcompile.cc",
        "extensions/stringcompilescript.cc",
        "extensions/stringfile.cc",
        "extensions/stringmapscript.cc",
        "extensions/stringprintscript.cc",
        "extensions/stringutil.cc",
    ],
)


this_directory = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
with (this_directory / "README.md").open(encoding="utf8") as source:
  long_description = source.read()


def get_version(rel_path):
  # Searches through a file to find a `__version__ = "X.Y.Z"` string.
  # From https://packaging.python.org/guides/single-sourcing-package-version/.
  with (this_directory / rel_path).open(encoding="utf8") as fp:
    for line in fp:
      if line.startswith("__version__"):
        delim = '"' if '"' in line else "'"
        return line.split(delim)[1]
    else:
      raise RuntimeError("Unable to find version string.")


__version__ = get_version("pynini/__init__.py")


def main() -> None:
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
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
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
      install_requires=["Cython >= 0.29"],
      ext_modules=cythonize([pywrapfst, pynini]),
      packages=find_packages(exclude=["scripts", "tests"]),
      package_data={
          "pywrapfst": ["__init__.pyi", "py.typed"],
          "pynini": ["__init__.pyi", "py.typed"],
          "pynini.examples": ["py.typed"],
          "pynini.export": ["py.typed"],
          "pynini.lib": ["py.typed"],
      },
      zip_safe=False,
  )


if __name__ == "__main__":
  main()
