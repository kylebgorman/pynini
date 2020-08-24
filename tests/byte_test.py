# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests for byte.py."""

import string

import pynini
from pynini.lib import byte
import unittest


class ByteTest(unittest.TestCase):

  def assertAccepts(self, s: str, fst: pynini.Fst) -> None:
    intersection = s @ fst
    self.assertNotEqual(intersection.start(), pynini.NO_STATE_ID)

  def testAsciiBytes(self) -> None:
    for char in range(1, 128):
      self.assertAccepts(pynini.escape(chr(char)), byte.BYTES)

  def testSuperAsciiBytes(self) -> None:
    for char in range(128, 256):
      self.assertAccepts(f"[{char}]", byte.BYTES)

  def testDigit(self) -> None:
    for s in string.digits:
      self.assertAccepts(s, byte.BYTES)

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

  # TODO(kbg): Add tests for SPACE, NOT_SPACE, PUNCT, NOT_QUOTE, and GRAPH.


if __name__ == "__main__":
  unittest.main()

