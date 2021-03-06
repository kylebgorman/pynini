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

# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests for byte.py."""

import string

import pynini
from pynini.lib import byte
from absl.testing import absltest


class ByteTest(absltest.TestCase):

  def assertAccepts(self, s: str, fst: pynini.Fst) -> None:
    intersection = s @ fst
    self.assertNotEqual(intersection.start(), pynini.NO_STATE_ID)

  def testAsciiBytes(self) -> None:
    for char in range(1, 128):
      self.assertAccepts(pynini.escape(chr(char)), byte.BYTE)

  def testSuperAsciiBytes(self) -> None:
    for char in range(128, 256):
      self.assertAccepts(f"[{char}]", byte.BYTE)

  def testDigit(self) -> None:
    for s in string.digits:
      self.assertAccepts(s, byte.BYTE)

  def testLower(self) -> None:
    for s in string.ascii_lowercase:
      self.assertAccepts(s, byte.LOWER)

  def testUpper(self) -> None:
    for s in string.ascii_uppercase:
      self.assertAccepts(s, byte.UPPER)

  def testAlpha(self) -> None:
    for s in string.ascii_letters:
      self.assertAccepts(s, byte.ALPHA)

  def testHex(self) -> None:
    for s in string.hexdigits:
      self.assertAccepts(s, byte.HEX)

  def testPunct(self) -> None:
    for s in string.punctuation:
      self.assertAccepts(pynini.escape(s), byte.PUNCT)

  # TODO(kbg): Add tests for SPACE, NOT_SPACE, NOT_QUOTE, and GRAPH.


if __name__ == "__main__":
  absltest.main()

