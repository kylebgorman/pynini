# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests pynutil."""

import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite

import unittest


class UtilitiesTest(unittest.TestCase):

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


if __name__ == "__main__":
  unittest.main()

