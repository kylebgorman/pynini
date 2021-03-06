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
"""Tests for utf8.py."""

import pynini
from pynini.lib import byte
from pynini.lib import utf8
from absl.testing import absltest

ASCII_STRINGS = ["ha ha", "who?", "Capitals!", "`1234567890~!@#$%^&*()"]
NON_ASCII_CHARS = ["é", "ב", "क", "€", "д", "零"]
UTF8_STRINGS = ["Who?", "¿Quién?", "ארה״ב", "हिन्दी", "今日はそれがググりました。"]


class Utf8Test(absltest.TestCase):

  def is_subset(self, string: pynini.FstLike, fsa: pynini.Fst) -> bool:
    fsa = pynini.determinize(fsa.copy().rmepsilon())
    string_union_fsa = pynini.determinize(pynini.union(fsa, string).rmepsilon())
    return pynini.equivalent(string_union_fsa, fsa)

  def all_prefixes(self, fsa: pynini.Fst) -> pynini.Fst:
    fsa = fsa.copy()
    for s in fsa.states():
      fsa.set_final(s)
    return fsa.optimize()

  def all_suffixes(self, fsa: pynini.Fst) -> pynini.Fst:
    fsa = fsa.copy()
    start_state = fsa.start()
    for s in fsa.states():
      fsa.add_arc(start_state,
                  pynini.Arc(0, 0, pynini.Weight.one(fsa.weight_type()), s))
    return fsa.optimize()

  def all_substrings(self, fsa: pynini.Fst) -> pynini.Fst:
    fsa = fsa.copy()
    start_state = fsa.start()
    for s in fsa.states():
      fsa.set_final(s)
      fsa.add_arc(start_state,
                  pynini.Arc(0, 0, pynini.Weight.one(fsa.weight_type()), s))
    return fsa.optimize()

  def all_single_byte_prefixes(self, fsa: pynini.Fst) -> pynini.Fst:
    return pynini.intersect(self.all_prefixes(fsa), byte.BYTE).optimize()

  def all_single_byte_suffixes(self, fsa: pynini.Fst) -> pynini.Fst:
    return pynini.intersect(self.all_suffixes(fsa), byte.BYTE).optimize()

  def all_single_byte_substrings(self, fsa: pynini.Fst) -> pynini.Fst:
    return pynini.intersect(self.all_substrings(fsa), byte.BYTE).optimize()

  def assertIsFsa(self, fsa: pynini.Fst) -> None:
    if fsa.properties(pynini.ACCEPTOR, True) != pynini.ACCEPTOR:
      raise AssertionError(f"Expected {fsa} to be an acceptor")

  def assertStrInAcceptorLanguage(self, string: pynini.FstLike,
                                  fst: pynini.Fst) -> None:
    self.assertIsFsa(fst)
    if not self.is_subset(string, fst):
      raise AssertionError(
          f"Expected {string} to be in the language defined by {fst}"
      )

  def assertStrNotInAcceptorLanguage(self, string: pynini.FstLike,
                                     fst: pynini.Fst) -> None:
    self.assertIsFsa(fst)
    if self.is_subset(string, fst):
      raise AssertionError(
          f"Expected {string} to not be in the language defined by {fst}"
      )

  def assertFsasEquivalent(self, fsa1: pynini.Fst, fsa2: pynini.Fst) -> None:
    self.assertIsFsa(fsa1)
    self.assertIsFsa(fsa2)
    fsa1 = pynini.determinize(pynini.rmepsilon(fsa1))
    fsa2 = pynini.determinize(pynini.rmepsilon(fsa2))
    if not pynini.equivalent(fsa1, fsa2):
      raise AssertionError(f"Expected {fsa1} and {fsa2} to be equivalent")

  def testAsciiStringsAgainstValidSingleByte(self) -> None:
    for string in ASCII_STRINGS:
      self.assertStrNotInAcceptorLanguage(string, utf8.SINGLE_BYTE)
      self.assertStrInAcceptorLanguage(string, utf8.SINGLE_BYTE.star)

  def testKnownCharsNotLeadingContinuationByte(self) -> None:
    for char in NON_ASCII_CHARS:
      self.assertStrNotInAcceptorLanguage(char, utf8.LEADING_BYTE)
      self.assertStrNotInAcceptorLanguage(char, utf8.CONTINUATION_BYTE)

  def testKnownCharsValidUtf8Char(self) -> None:
    for char in NON_ASCII_CHARS:
      self.assertStrInAcceptorLanguage(char, utf8.VALID_UTF8_CHAR)
      self.assertStrNotInAcceptorLanguage(char * 2, utf8.VALID_UTF8_CHAR)
      self.assertStrNotInAcceptorLanguage(char * 3, utf8.VALID_UTF8_CHAR)

  def testUtf8StringsNotValidUtf8Char(self) -> None:
    for string in UTF8_STRINGS:
      self.assertStrNotInAcceptorLanguage(string, utf8.VALID_UTF8_CHAR)

  def testValidUtf8Strings(self) -> None:
    for string in UTF8_STRINGS + NON_ASCII_CHARS:
      self.assertStrInAcceptorLanguage(string, utf8.VALID_UTF8_CHAR.star)

  def testVerifyAsciiDefinition(self):
    ascii_char = pynini.string_map(
        # UTF-8 ASCII uses the all single byte characters with most
        # significant bit set to 0, barring NUL, which we ignore.
        pynini.escape(chr(codepoint))
        for codepoint in range(1, 128)).optimize()
    self.assertFsasEquivalent(ascii_char, utf8.SINGLE_BYTE)

  def testVerifyLeadingBytesDefinition(self):
    # The leading bytes should be all single byte prefixes of valid UTF-8
    # characters barring the legal single byte characters (ASCII).
    leading_bytes = self.all_single_byte_prefixes(
        utf8.VALID_UTF8_CHAR) - utf8.SINGLE_BYTE
    self.assertFsasEquivalent(leading_bytes, utf8.LEADING_BYTE)

  def testVerifyContinuationBytesDefinition(self):
    # The continuation bytes should be all single byte suffixes of valid UTF-8
    # characters barring the legal single byte characters (ASCII).
    continue_bytes = self.all_single_byte_suffixes(
        utf8.VALID_UTF8_CHAR) - utf8.SINGLE_BYTE
    self.assertFsasEquivalent(continue_bytes, utf8.CONTINUATION_BYTE)

  def testVerifyValidBytesDefinition(self):
    valid_bytes = self.all_single_byte_substrings(utf8.VALID_UTF8_CHAR)
    self.assertFsasEquivalent(valid_bytes, utf8.VALID_BYTE)

  def testVerifyUtf8Rfc3629Definition(self):
    utf8_rfc3629_char = pynini.string_map(
        # UTF-8 encoded strings can store codepoints in U+0000 through
        # U+0x10FFFF, excluding the surrogate halves in U+D800 through
        # U+DFFF, but we exclude U+0000 as it would be strange to match NUL
        # and that label is reserved for epsilon.
        pynini.escape(chr(codepoint))
        for codepoint in range(1, 0x10FFFF + 1)
        if not 0xD800 <= codepoint <= 0xDFFF).optimize()
    self.assertFsasEquivalent(utf8_rfc3629_char, utf8.VALID_UTF8_CHAR)

  def testVerifyUtf8CharRegionalIndicatorSymbolDefinition(self):
    regional_indicator = pynini.string_map(
        # Regional indicator symbols have codepoints in the range 0x1F1E6
        # through 0x1F1FF.
        pynini.escape(chr(codepoint))
        for codepoint in range(0x1F1E6, 0x1F1FF + 1)).optimize()
    self.assertFsasEquivalent(regional_indicator,
                              utf8.VALID_UTF8_CHAR_REGIONAL_INDICATOR_SYMBOL)

  def testVerifyAsciiInUtf8(self):
    self.assertStrInAcceptorLanguage(utf8.SINGLE_BYTE, utf8.VALID_UTF8_CHAR)

  def testVerifyRegionalIndicatorSymbolInUtf8(self):
    self.assertStrInAcceptorLanguage(
        utf8.VALID_UTF8_CHAR_REGIONAL_INDICATOR_SYMBOL, utf8.VALID_UTF8_CHAR)


if __name__ == "__main__":
  absltest.main()

