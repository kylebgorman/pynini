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
"""Tests pynutil."""

import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite

from absl.testing import absltest


class UtilitiesTest(absltest.TestCase):

  # TD-deletion in English, expressed as a mandatory rule.

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

  def testJoin(self):
    joined = pynutil.join("a", " ")
    for i in range(1, 10):
      query = " ".join(["a"] * i)
      lattice = pynini.intersect(joined, query)
      self.assertNotEqual(lattice.start(), pynini.NO_STATE_ID)


if __name__ == "__main__":
  absltest.main()

