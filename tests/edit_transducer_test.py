# Lint as: python3
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


class LevenshteinAutomatonTest(absltest.TestCase):
  automaton: edit_transducer.LevenshteinAutomaton
  distance: edit_transducer.LevenshteinDistance

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cheese_lexicon = [
        "tilsit", "caerphilly", "stilton", "gruyere", "emmental", "liptauer",
        "lancashire", "cheshire", "brie", "roquefort", "savoyard", "boursin",
        "camembert", "gouda", "edam", "caithness", "wensleydale", "gorgonzola",
        "parmesan", "mozzarella", "fynbo", "cheddar", "ilchester", "limburger"
    ]
    cls.automaton = edit_transducer.LevenshteinAutomaton(
        string.ascii_lowercase, cheese_lexicon)
    cls.distance = edit_transducer.LevenshteinDistance(string.ascii_lowercase)

  def query_and_distance(self, query, expected_closest, expected_distance):
    closest = self.automaton.closest_match(query)
    self.assertEqual(expected_closest, closest)
    distance = self.distance.distance(query, closest)
    self.assertEqual(expected_distance, distance)

  ## Tests using query_and_distance helper.

  def testMatch(self):
    self.query_and_distance("stilton", "stilton", 0.0)

  def testInsertion(self):
    self.query_and_distance("mozarela", "mozzarella", 2.0)

  def testDeletion(self):
    self.query_and_distance("emmenthal", "emmental", 1.0)

  def testSubstitution(self):
    self.query_and_distance("bourzin", "boursin", 1.0)

  def testMixedEdit(self):
    self.query_and_distance("rockford", "roquefort", 4.0)

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


if __name__ == "__main__":
  absltest.main()

