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
"""Tests edit transducer classes (specifically, the Levenshtein automaton)."""

import string

from absl.testing import absltest

from pynini.lib import edit_transducer


ALPHABET = string.ascii_lowercase
LEXICON = [
    "tilsit", "caerphilly", "stilton", "gruyere", "emmental", "liptauer",
    "lancashire", "cheshire", "brie", "roquefort", "savoyard", "boursin",
    "camembert", "gouda", "edam", "caithness", "wensleydale", "gorgonzola",
    "parmesan", "mozzarella", "fynbo", "cheddar", "ilchester", "limburger"
]


class EditTest(absltest.TestCase):
  automaton: edit_transducer.LevenshteinAutomaton
  distance: edit_transducer.LevenshteinDistance

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.automaton = edit_transducer.LevenshteinAutomaton(
        iter(ALPHABET), LEXICON)
    cls.distance = edit_transducer.LevenshteinDistance(iter(ALPHABET))

  def query_and_distance(self, query: str, expected_closest: str,
                         expected_distance: float) -> None:
    closest = self.automaton.closest_match(query)
    self.assertEqual(expected_closest, closest)
    distance = self.distance.distance(query, closest)
    self.assertEqual(expected_distance, distance)

  ## Tests using query_and_distance helper.

  def testMatch(self):
    self.query_and_distance("stilton", "stilton", 0)

  def testInsertion(self):
    self.query_and_distance("mozarela", "mozzarella", 2)

  def testDeletion(self):
    self.query_and_distance("emmenthal", "emmental", 1)

  def testSubstitution(self):
    self.query_and_distance("bourzin", "boursin", 1)

  def testMixedEdit(self):
    self.query_and_distance("rockford", "roquefort", 4)

  ## Other tests.

  def testClosestMatchFindsExactMatch(self):
    res = self.automaton.closest_matches("cheddar")
    self.assertSameElements(("cheddar",), res)

  def testClosestMatchReturnsMultiple(self):
    res = self.automaton.closest_matches("cheese")
    self.assertSameElements(("cheddar", "cheshire"), res)

  def testOutOfAlphabetQueryRaisesError(self):
    with self.assertRaises(edit_transducer.Error):
      unused_closest = self.automaton.closest_match("Gruyère")


class BoundEditTest(absltest.TestCase):
  """Same as above but with a bound of 2."""
  automaton: edit_transducer.LevenshteinAutomaton
  distance: edit_transducer.LevenshteinDistance

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.automaton = edit_transducer.LevenshteinAutomaton(
        iter(ALPHABET), LEXICON, bound=2)
    cls.distance = edit_transducer.LevenshteinDistance(iter(ALPHABET), bound=2)

  def query_and_distance(self, query: str, expected_closest: str,
                         expected_distance: float) -> None:
    closest = self.automaton.closest_match(query)
    self.assertEqual(expected_closest, closest)
    distance = self.distance.distance(query, closest)
    self.assertEqual(expected_distance, distance)

  ## Tests using query_and_distance helper.

  def testMatch(self):
    self.query_and_distance("stilton", "stilton", 0)

  def testInsertion(self):
    self.query_and_distance("mozarela", "mozzarella", 2)

  def testDeletion(self):
    self.query_and_distance("emmenthal", "emmental", 1)

  def testSubstitution(self):
    self.query_and_distance("bourzin", "boursin", 1)

  def testMixedEdit(self):
    # These will fail because they exceed the bound.
    with self.assertRaises(edit_transducer.Error):
      unused_closest = self.automaton.closest_match("rockford")
    with self.assertRaises(edit_transducer.Error):
      unused_distance = self.distance.distance("rockford", "roquefort")


if __name__ == "__main__":
  absltest.main()

