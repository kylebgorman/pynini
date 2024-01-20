# Copyright 2016-2024 Google LLC
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
"""Utility file for automatically generating Stringfiles for Pynini and Thrax.

This file exposes a `stringfile.escape` function which can be used to escape a
string literal for use as a field in a stringfile as well as a
`stringfile.writeline` and `stringfile.writelines` to use in a similar way to
`csv.writer.writerow` and `csv.writer.writerows`.
"""

from typing import IO, Iterable

import logging

import pynini

_special_chars_map = str.maketrans({"#": "\\#"})


def escape(string: str) -> str:
  """Escapes #-comments and backslashes and square brackets for stringfiles."""
  return pynini.escape(string).translate(_special_chars_map)


def writeline(file: IO[str], line: Iterable[str]) -> None:
  """Appends a stringfile line onto the end of an existing writable file.

  Args:
    file: The file (or file-like object) to append to.
    line: A string iterable of length between 1 and 3 inclusive of fields to
          place into the stringfile.
  """
  escaped_fields = [escape(field) for field in line]
  if not 1 <= len(escaped_fields) <= 3:
    logging.error("Line `%s` has unexpected number of fields, %d",
                  ",".join(line), len(escaped_fields))
  print("\t".join(escaped_fields), file=file)


def writelines(file: IO[str], lines: Iterable[Iterable[str]]) -> None:
  """Appends stringfile lines onto the end of an existing writable file.

  Args:
    file: The file (or file-like object) to append to.
    lines: An iterable of length 1 to 3 inclusive string iterables of fields to
           place into the stringfile (See `writeline`).
  """
  for line in lines:
    writeline(file, line)

