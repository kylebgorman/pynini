# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests rewrite functions."""

import string

import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite

import unittest


# Some phonological classes expressed as FSAs.


SIGMA_STAR = pynini.union(*string.ascii_lowercase).closure().optimize()
TD = pynini.union("t", "d")
CONSONANT = pynini.union(TD, "p", "b", "f", "v", "s", "z", "k", "g", "m", "n",
                         "l", "r").optimize()


class RewriteTest(unittest.TestCase):

  # TD-deletion in English, expressed as a mandatory rule.

  def testSimpleRewrite(self):
    rule = pynini.cdrewrite(pynutil.delete(TD), CONSONANT, "[EOS]",
                            SIGMA_STAR).optimize()
    rewrites = tuple(rewrite.rewrites("fist", rule))
    # pylint: disable=g-generic-assert
    self.assertEqual(len(rewrites), 1)
    # pylint: enable=g-generic-assert
    self.assertEqual("fis", rewrites[0])
    self.assertEqual("fis", rewrite.top_rewrite("fist", rule))
    self.assertEqual("fis", rewrite.one_top_rewrite("fist", rule))
    self.assertTrue(rewrite.matches("fist", "fis", rule))
    self.assertFalse(rewrite.matches("fis", "fist", rule))

  # TD-deletion in English, expressed as a optional rule, so that application
  # and non-application are tied.

  def testTiedRewrite(self):
    rule = pynini.cdrewrite(
        pynutil.delete(TD), CONSONANT, "[EOS]", SIGMA_STAR,
        mode="opt").optimize()
    with self.assertRaisesRegex(rewrite.Error, r"Multiple top rewrites"):
      unused_var = rewrite.one_top_rewrite("fist", rule)

  # Made-up rule cascade in which consonant cluster simplification:
  #
  # C -> 0 / __ C
  #
  # outranks epenthesis to avoid the cluster:
  #
  # 0 -> i / C __ C.
  #
  # Because of this ranking, there's no tie.

  def testRankedRewrite(self):
    deletion_rule = pynini.cdrewrite(
        pynutil.delete(CONSONANT, weight=1), "", CONSONANT, SIGMA_STAR)
    epenthesis_rule = pynini.cdrewrite(
        pynutil.insert("i", weight=2), CONSONANT, CONSONANT, SIGMA_STAR)
    rule = pynini.union(deletion_rule, epenthesis_rule).optimize()
    self.assertEqual("oto", rewrite.one_top_rewrite("okto", rule))
    self.assertTrue(rewrite.matches("okto", "oto", rule))

  # TD-deletion, expressed as an optional rule, so that we get two optimal
  # rewrites.

  def testOptionalRewrite(self):
    rule = pynini.cdrewrite(
        pynutil.delete(TD), CONSONANT, "[EOS]", SIGMA_STAR,
        mode="opt").optimize()
    self.assertCountEqual(["fist", "fis"], rewrite.rewrites("fist", rule))
    self.assertTrue(rewrite.matches("fist", "fis", rule))
    self.assertTrue(rewrite.matches("fist", "fist", rule))
    self.assertFalse(rewrite.matches("fis", "fist", rule))


if __name__ == "__main__":
  unittest.main()

