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
"""Tests for the chatspeak model."""

import os
from typing import List

from absl import flags

import pynini
from pynini.examples import chatspeak
from pynini.lib import rewrite
from absl.testing import absltest

FLAGS = flags.FLAGS


class ChatspeakTest(absltest.TestCase):

  deduplicator: chatspeak.Deduplicator
  deabbreviator: chatspeak.Deabbreviator
  regexps: chatspeak.Regexps
  lexicon: chatspeak.Lexicon

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    lexicon = pynini.union("the", "cool", "warthog", "escaped", "easily",
                           "from", "baltimore", "zoo", "col")
    cls.deduplicator = chatspeak.Deduplicator(lexicon)
    cls.deabbreviator = chatspeak.Deabbreviator(lexicon)
    cls.regexps = chatspeak.Regexps()
    # Set the directory to org_opengrm_pynini/tests/testdata" for Bazel testing.
    cls.lexicon = chatspeak.Lexicon(
        os.path.join(
            FLAGS.test_srcdir, "tests/"
            "testdata/chatspeak_lexicon.tsv"))

  def testDeduplicator(self):

    def expand_string(s: str) -> List[str]:
      return rewrite.lattice_to_strings(self.deduplicator.expand(s))

    self.assertSameElements(expand_string("cooooool"), ["cool", "col"])
    self.assertSameElements(
        expand_string("coooooooooooooooollllllllll"), ["cool", "col"])
    self.assertSameElements(expand_string("chicken"), [])

  def testDeabbreviator(self):

    def expand_string(s: str) -> List[str]:
      return rewrite.lattice_to_strings(self.deabbreviator.expand(s))

    self.assertSameElements(expand_string("wrthg"), ["warthog"])
    self.assertSameElements(expand_string("wthg"), ["warthog"])
    self.assertSameElements(expand_string("z"), [])

  def testRegexps(self):

    def expand_string(s: str) -> List[str]:
      return rewrite.lattice_to_strings(self.regexps.expand(s))

    result = expand_string("delish")
    self.assertSameElements(result, ["delicious"])
    result = expand_string("kooooooooool")
    self.assertSameElements(result, ["cool"])
    result = expand_string("zomgggggggg")
    self.assertSameElements(result, ["oh my god"])

  def testLexicon(self):

    def expand_string(s: str) -> List[str]:
      return rewrite.lattice_to_strings(self.lexicon.expand(s))

    self.assertSameElements(expand_string("1nam"), ["one in a million"])


if __name__ == "__main__":
  absltest.main()

