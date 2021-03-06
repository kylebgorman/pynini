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
"""Tests rule cascade."""

import os
import tempfile

import pynini
from pynini.lib import rule_cascade

from absl.testing import absltest


class RuleCascadeTest(absltest.TestCase):

  far_path: str
  cascade: rule_cascade.RuleCascade

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    fold = pynini.string_map((("A", "a"), ("B", "b"))).optimize()
    cls.far_path = tempfile.mkstemp(suffix=".far")[1]
    with pynini.Far(cls.far_path, "w") as far:
      far["DOWNCASE"] = fold
      far["UPCASE"] = fold.invert()
    cls.cascade = rule_cascade.RuleCascade(cls.far_path)

  @classmethod
  def tearDownClass(cls):
    os.remove(cls.far_path)
    super().tearDownClass()

  def testBadRuleRaisesException(self):
    with self.assertRaises(rule_cascade.Error):
      self.cascade.set_rules(["NOT_A_RULE"])

  def testGoodRuleCanBeSet(self):
    self.cascade.set_rules(["DOWNCASE"])

  def testSimple(self):
    self.cascade.set_rules(["DOWNCASE"])
    self.assertEqual(self.cascade.top_rewrite("A"), "a")
    self.assertEqual(self.cascade.one_top_rewrite("A"), "a")
    self.assertCountEqual(self.cascade.rewrites("A"), ["a"])
    self.assertCountEqual(self.cascade.top_rewrites("A", 100), ["a"])
    self.assertCountEqual(self.cascade.optimal_rewrites("A"), ["a"])
    self.assertTrue(self.cascade.matches("A", "a"))

  def testRoundtrip(self):
    self.cascade.set_rules(["DOWNCASE", "UPCASE"])
    self.assertEqual(self.cascade.top_rewrite("B"), "B")
    self.assertEqual(self.cascade.one_top_rewrite("B"), "B")
    self.assertCountEqual(self.cascade.rewrites("B"), ["B"])
    self.assertCountEqual(self.cascade.top_rewrites("B", 100), ["B"])
    self.assertCountEqual(self.cascade.optimal_rewrites("B"), ["B"])
    self.assertTrue(self.cascade.matches("B", "B"))


if __name__ == "__main__":
  absltest.main()

