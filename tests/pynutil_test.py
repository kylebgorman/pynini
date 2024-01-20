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
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests pynutil."""

import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite

from absl.testing import absltest


class UtilitiesTest(absltest.TestCase):

  def testUnweightedInsert(self):
    inserter = pynutil.insert("Cheddar")
    self.assertEqual(rewrite.one_top_rewrite("", inserter), "Cheddar")

  def testUnweightedDelete(self):
    deleter = pynutil.delete("Cheddar")
    self.assertEqual(rewrite.one_top_rewrite("Cheddar", deleter), "")

  def total_weight(self, fst: pynini.Fst) -> float:
    return float(pynini.shortestdistance(fst, reverse=True)[fst.start()])

  def testWeightedInsert(self):
    inserter = pynutil.insert("Cheddar", 2)
    self.assertEqual(self.total_weight(inserter), 2)

  def testWeightedDelete(self):
    deleter = pynutil.delete("Cheddar", 2)
    self.assertEqual(self.total_weight(deleter), 2)

  def testAddUntypedWeightToUntypedExpression(self):
    # Mismatch is impossible here.
    cheese = pynutil.add_weight("Cheddar", 2)
    self.assertEqual(cheese.weight_type(), "tropical")

  def testAddUntypedWeightToTypedExpression(self):
    # Mismatch is impossible here.
    cheese = pynini.accep("Cheddar", arc_type="log")
    cheese = pynutil.add_weight(cheese, 2)
    self.assertEqual(cheese.weight_type(), "log")

  def testAddTypedWeightToUntypedExpression(self):
    # No mismatch because tropical comes from the default context.
    weight = pynini.Weight("tropical", 2)
    cheese = pynutil.add_weight("Cheddar", weight)
    self.assertEqual(cheese.weight_type(), "tropical")
    # Mismatch occurs here.
    weight = pynini.Weight("log", 2)
    with self.assertRaises(pynini.FstOpError):
      unused_cheese = pynutil.add_weight("Cheddar", weight)

  def testAddTypedWeightToTypedExpression(self):
    # No mismatch.
    cheese = pynini.accep("Cheddar", arc_type="log")
    weight = pynini.Weight("log", 2)
    cheese = pynutil.add_weight(cheese, weight)
    self.assertEqual(cheese.weight_type(), "log")
    # Mismatch occurs here.
    weight = pynini.Weight("tropical", 2)
    with self.assertRaises(pynini.FstOpError):
      unused_cheese = pynutil.add_weight(cheese, weight)

  def testJoin(self):
    joined = pynutil.join("a", " ")
    for i in range(1, 10):
      query = " ".join(["a"] * i)
      lattice = pynini.intersect(joined, query)
      self.assertNotEqual(lattice.start(), pynini.NO_STATE_ID)


if __name__ == "__main__":
  absltest.main()

