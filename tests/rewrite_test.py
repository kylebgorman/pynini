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
"""Tests rewrite functions."""

import string

import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite

from absl.testing import absltest


class DirectionalityTest(absltest.TestCase):
  """Tests cdrewrite rule directionality.

  The example is based on section 11.1 of:

      Bale, A., and Reiss, C. 2018. Phonology: A Formal Introduction. MIT Press.
  """

  sigstar: pynini.Fst
  tau: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.sigstar = pynini.union("a", "b").closure().optimize()
    cls.tau = pynini.cross("b", "a")

  def assertOneTopRewrite(self, istring: str, ostring: str,
                          rule: pynini.Fst) -> None:
    self.assertEqual(rewrite.one_top_rewrite(istring, rule), ostring)

  def assertUnambiguousExamples(self, rule: pynini.Fst) -> None:
    # All three rules behave the same regardless of directionality.
    self.assertOneTopRewrite("bbba", "baba", rule)
    self.assertOneTopRewrite("abbabbba", "abbababa", rule)
    self.assertOneTopRewrite("abbbabbba", "ababababa", rule)

  def testLeftToRightApplication(self):
    rule = pynini.cdrewrite(
        self.tau, "b", "b", self.sigstar, direction="ltr").optimize()
    self.assertUnambiguousExamples(rule)
    self.assertOneTopRewrite("abbbba", "ababba", rule)

  def testRightToLeftApplication(self):
    rule = pynini.cdrewrite(
        self.tau, "b", "b", self.sigstar, direction="rtl").optimize()
    self.assertUnambiguousExamples(rule)
    self.assertOneTopRewrite("abbbba", "abbaba", rule)

  def testSimultaneousApplication(self):
    rule = pynini.cdrewrite(
        self.tau, "b", "b", self.sigstar, direction="sim").optimize()
    self.assertUnambiguousExamples(rule)
    self.assertOneTopRewrite("abbbba", "abaaba", rule)


class TDTest(absltest.TestCase):
  """Two forms of /t, d/-deletion."""

  sigstar: pynini.Fst
  td: pynini.Fst
  consonant: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.sigstar = pynini.union(*string.ascii_lowercase).closure().optimize()
    cls.td = pynini.union("t", "d").optimize()
    cls.consonant = pynini.union(cls.td, "p", "b", "f", "v", "s", "z", "k", "g",
                                 "m", "n", "l", "r").optimize()

  def testMandatoryRewrite(self):
    rule = pynini.cdrewrite(
        pynutil.delete(self.td), self.consonant, "[EOS]",
        self.sigstar).optimize()
    rewrites = tuple(rewrite.rewrites("fist", rule))
    # pylint: disable=g-generic-assert
    self.assertEqual(len(rewrites), 1)
    # pylint: enable=g-generic-assert
    self.assertEqual("fis", rewrites[0])
    self.assertEqual("fis", rewrite.top_rewrite("fist", rule))
    self.assertEqual("fis", rewrite.one_top_rewrite("fist", rule))
    self.assertTrue(rewrite.matches("fist", "fis", rule))
    self.assertFalse(rewrite.matches("fis", "fist", rule))

  def testOptionalRewrite(self):
    rule = pynini.cdrewrite(
        pynutil.delete(self.td),
        self.consonant,
        "[EOS]",
        self.sigstar,
        mode="opt").optimize()
    with self.assertRaisesRegex(rewrite.Error, r"Multiple top rewrites"):
      unused_var = rewrite.one_top_rewrite("fist", rule)
    self.assertCountEqual(["fist", "fis"], rewrite.rewrites("fist", rule))
    self.assertTrue(rewrite.matches("fist", "fis", rule))
    self.assertTrue(rewrite.matches("fist", "fist", rule))
    self.assertFalse(rewrite.matches("fis", "fist", rule))


class RankedTest(absltest.TestCase):
  """Made-up rule cascade in which consonant cluster simplification:

      C -> 0 / __ C

  outranks epenthesis to avoid the cluster:

      0 -> i / C __ C.

  Because of this ranking, there's no tie.
  """

  sigstar: pynini.Fst
  consonant: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.sigstar = pynini.union(*string.ascii_lowercase).closure().optimize()
    cls.consonant = pynini.union("p", "b", "f", "v", "t", "d", "s", "z", "k",
                                 "g", "m", "n", "l", "r").optimize()

  def testRankedRewrite(self):
    deletion_rule = pynini.cdrewrite(
        pynutil.delete(self.consonant, weight=1), "", self.consonant,
        self.sigstar)
    epenthesis_rule = pynini.cdrewrite(
        pynutil.insert("i", weight=2), self.consonant, self.consonant,
        self.sigstar)
    rule = pynini.union(deletion_rule, epenthesis_rule).optimize()
    self.assertEqual("oto", rewrite.one_top_rewrite("okto", rule))
    self.assertTrue(rewrite.matches("okto", "oto", rule))


if __name__ == "__main__":
  absltest.main()

