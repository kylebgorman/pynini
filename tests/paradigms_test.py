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
"""Tests for Paradigms."""

from absl.testing import absltest

import pynini
from pynini.lib import features
from pynini.lib import paradigms
from pynini.lib import pynutil
from pynini.lib import rewrite


class LatinFirstDeclensionNounTest(absltest.TestCase):
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    num = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    noun = features.Category(case, num)
    nomsg = features.FeatureVector(noun, "case=nom", "num=sg")
    stem = paradigms.make_byte_star_except_boundary()
    slots = [(paradigms.suffix("+a", stem), nomsg),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=gen", "num=sg")),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=dat", "num=sg")),
             (paradigms.suffix("+am", stem),
              features.FeatureVector(noun, "case=acc", "num=sg")),
             (paradigms.suffix("+ā", stem),
              features.FeatureVector(noun, "case=abl", "num=sg")),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=nom", "num=pl")),
             (paradigms.suffix("+ārum", stem),
              features.FeatureVector(noun, "case=gen", "num=pl")),
             (paradigms.suffix("+īs", stem),
              features.FeatureVector(noun, "case=dat", "num=pl")),
             (paradigms.suffix("+ās", stem),
              features.FeatureVector(noun, "case=acc", "num=pl")),
             (paradigms.suffix("+īs", stem),
              features.FeatureVector(noun, "case=abl", "num=pl"))]
    cls.paradigm = paradigms.Paradigm(
        category=noun,
        slots=slots,
        lemma_feature_vector=nomsg,
        stems=["aqu", "bell", "caus", "cicād", "mens", "naut", "puell"])

  def testGenerator(self):
    generator = (
        self.paradigm.stems_to_forms @ self.paradigm.feature_label_rewriter)
    forms = rewrite.rewrites("aqu", generator)
    self.assertSameElements([
        "aqu+a[case=nom][num=sg]", "aqu+ae[case=gen][num=sg]",
        "aqu+ae[case=dat][num=sg]", "aqu+am[case=acc][num=sg]",
        "aqu+ā[case=abl][num=sg]", "aqu+ae[case=nom][num=pl]",
        "aqu+ārum[case=gen][num=pl]", "aqu+īs[case=dat][num=pl]",
        "aqu+ās[case=acc][num=pl]", "aqu+īs[case=abl][num=pl]"
    ], forms)

  def testAnalyzer(self):
    self.assertSameElements([("aqu+ārum",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm.analyze("aquārum"))
    self.assertSameElements([
        ("puell+īs",
         features.FeatureVector(self.paradigm.category, "case=dat", "num=pl")),
        ("puell+īs",
         features.FeatureVector(self.paradigm.category, "case=abl", "num=pl"))
    ], self.paradigm.analyze("puellīs"))

  def testTagger(self):
    self.assertSameElements([("aquārum",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm.tag("aquārum"))
    self.assertSameElements([
        ("puellīs",
         features.FeatureVector(self.paradigm.category, "case=dat", "num=pl")),
        ("puellīs",
         features.FeatureVector(self.paradigm.category, "case=abl", "num=pl"))
    ], self.paradigm.tag("puellīs"))

  def testLemmatizer(self):
    self.assertSameElements([("aqua",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm.lemmatize("aquārum"))
    self.assertSameElements([
        ("puella",
         features.FeatureVector(self.paradigm.category, "case=dat", "num=pl")),
        ("puella",
         features.FeatureVector(self.paradigm.category, "case=abl", "num=pl")),
    ], self.paradigm.lemmatize("puellīs"))

  def testInflector(self):
    self.assertSameElements(["aquārum"],
                            self.paradigm.inflect(
                                "aqua",
                                features.FeatureVector(self.paradigm.category,
                                                       "case=gen", "num=pl")))
    self.assertSameElements(["puellīs"],
                            self.paradigm.inflect(
                                "puella",
                                features.FeatureVector(self.paradigm.category,
                                                       "case=dat", "num=pl")))


class LatinFirstDeclensionNounWildcardTest(absltest.TestCase):
  r"""An example of using \Sigma^* as a stem definition."""

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    number = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    noun = features.Category(case, number)
    nomsg = features.FeatureVector(noun, "case=nom", "num=sg")
    stem = paradigms.make_byte_star_except_boundary()
    slots = [(paradigms.suffix("+a", stem), nomsg),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=gen", "num=sg")),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=dat", "num=sg")),
             (paradigms.suffix("+am", stem),
              features.FeatureVector(noun, "case=acc", "num=sg")),
             (paradigms.suffix("+ā", stem),
              features.FeatureVector(noun, "case=abl", "num=sg")),
             (paradigms.suffix("+ae", stem),
              features.FeatureVector(noun, "case=nom", "num=pl")),
             (paradigms.suffix("+ārum", stem),
              features.FeatureVector(noun, "case=gen", "num=pl")),
             (paradigms.suffix("+īs", stem),
              features.FeatureVector(noun, "case=dat", "num=pl")),
             (paradigms.suffix("+ās", stem),
              features.FeatureVector(noun, "case=acc", "num=pl")),
             (paradigms.suffix("+īs", stem),
              features.FeatureVector(noun, "case=abl", "num=pl"))]
    v = pynini.union("a", "i", "e", "o", "u")
    c = pynini.union("b", "c", "d", "f", "g", "h", "l", "m", "n", "p", "q", "r",
                     "s", "t")
    cls.paradigm = paradigms.Paradigm(
        category=noun,
        slots=slots,
        lemma_feature_vector=nomsg,
        stems=[(v | c).closure(1)])

  def testGenerator(self):
    generator = (
        self.paradigm.stems_to_forms @ self.paradigm.feature_label_rewriter)
    forms = rewrite.rewrites("aqu", generator)
    self.assertSameElements([
        "aqu+a[case=nom][num=sg]", "aqu+ae[case=gen][num=sg]",
        "aqu+ae[case=dat][num=sg]", "aqu+am[case=acc][num=sg]",
        "aqu+ā[case=abl][num=sg]", "aqu+ae[case=nom][num=pl]",
        "aqu+ārum[case=gen][num=pl]", "aqu+īs[case=dat][num=pl]",
        "aqu+ās[case=acc][num=pl]", "aqu+īs[case=abl][num=pl]"
    ], forms)


class LatinThirdDeclensionNounTest(absltest.TestCase):
  """Certain consonant-final non-neuter stems."""
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    num = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    noun = features.Category(case, num)
    nomsg = features.FeatureVector(noun, "case=nom", "num=sg")
    stem = paradigms.make_byte_star_except_boundary()
    slots = [(paradigms.suffix("+s", stem), nomsg),
             (paradigms.suffix("+is", stem),
              features.FeatureVector(noun, "case=gen", "num=sg")),
             (paradigms.suffix("+ī", stem),
              features.FeatureVector(noun, "case=dat", "num=sg")),
             (paradigms.suffix("+em", stem),
              features.FeatureVector(noun, "case=acc", "num=sg")),
             (paradigms.suffix("+e", stem),
              features.FeatureVector(noun, "case=abl", "num=sg")),
             (paradigms.suffix("+ēs", stem),
              features.FeatureVector(noun, "case=nom", "num=pl")),
             (paradigms.suffix("+um", stem),
              features.FeatureVector(noun, "case=gen", "num=pl")),
             (paradigms.suffix("+ibus", stem),
              features.FeatureVector(noun, "case=dat", "num=pl")),
             (paradigms.suffix("+ēs", stem),
              features.FeatureVector(noun, "case=acc", "num=pl")),
             (paradigms.suffix("+ibus", stem),
              features.FeatureVector(noun, "case=abl", "num=pl"))]
    velar = pynini.union("c", "ct", "g")
    v = pynini.union("a", "i", "ī", "e", "ē", "u")
    rules = [
        # c, ct, g -> x in nominative singular. Note the spelling of "cs" as "x"
        # in Latin breaks the segmentation. One might also consider representing
        # this as "c+s".
        pynini.cdrewrite(
            pynini.cross(velar + "+s", "x+"), "", "", noun.sigma_star),
        # Rhotacize /s/ prevocalically: a non-Gorman theory of this alternation.
        pynini.cdrewrite(pynini.cross("s", "r"), "", "+" + v, noun.sigma_star),
        # s+s -> s.
        pynini.cdrewrite(pynini.cross("s+s", "s+"), "", "", noun.sigma_star)
    ]
    cls.paradigm = paradigms.Paradigm(
        category=noun,
        slots=slots,
        lemma_feature_vector=nomsg,
        stems=["noct", "ōs", "pac", "rēg"],
        rules=rules)

  def testGenerator(self):
    generator = (
        self.paradigm.stems_to_forms @ self.paradigm.feature_label_rewriter)
    forms = rewrite.rewrites("noct", generator)
    self.assertSameElements(
        [
            "nox+[case=nom][num=sg]",
            "noct+is[case=gen][num=sg]",
            "noct+ī[case=dat][num=sg]",
            "noct+em[case=acc][num=sg]",
            "noct+e[case=abl][num=sg]",
            "noct+ēs[case=nom][num=pl]",
            "noct+um[case=gen][num=pl]",  # TODO(rws): Actually "noctium".
            "noct+ibus[case=dat][num=pl]",
            "noct+ēs[case=acc][num=pl]",  # Also -īs for /i/ stems.
            "noct+ibus[case=abl][num=pl]"
        ],
        forms)
    forms = rewrite.rewrites("rēg", generator)
    self.assertSameElements([
        "rēx+[case=nom][num=sg]", "rēg+is[case=gen][num=sg]",
        "rēg+ī[case=dat][num=sg]", "rēg+em[case=acc][num=sg]",
        "rēg+e[case=abl][num=sg]", "rēg+ēs[case=nom][num=pl]",
        "rēg+um[case=gen][num=pl]", "rēg+ibus[case=dat][num=pl]",
        "rēg+ēs[case=acc][num=pl]", "rēg+ibus[case=abl][num=pl]"
    ], forms)
    forms = rewrite.rewrites("ōs", generator)
    self.assertSameElements([
        "ōs+[case=nom][num=sg]", "ōr+is[case=gen][num=sg]",
        "ōr+ī[case=dat][num=sg]", "ōr+em[case=acc][num=sg]",
        "ōr+e[case=abl][num=sg]", "ōr+ēs[case=nom][num=pl]",
        "ōr+um[case=gen][num=pl]", "ōr+ibus[case=dat][num=pl]",
        "ōr+ēs[case=acc][num=pl]", "ōr+ibus[case=abl][num=pl]"
    ], forms)

  def testAnalyzer(self):
    self.assertSameElements([("ōs+",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=nom", "num=sg"))],
                            self.paradigm.analyze("ōs"))
    self.assertSameElements([("rēg+e",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=abl", "num=sg"))],
                            self.paradigm.analyze("rēge"))

  def testTagger(self):
    self.assertSameElements([("ōs",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=nom", "num=sg"))],
                            self.paradigm.tag("ōs"))
    self.assertSameElements([("rēge",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=abl", "num=sg"))],
                            self.paradigm.tag("rēge"))

  def testLemmatizer(self):
    self.assertSameElements([("pax",
                              features.FeatureVector(self.paradigm.category,
                                                     "case=acc", "num=sg"))],
                            self.paradigm.lemmatize("pacem"))
    self.assertSameElements([
        ("nox",
         features.FeatureVector(self.paradigm.category, "case=dat", "num=pl")),
        ("nox",
         features.FeatureVector(self.paradigm.category, "case=abl", "num=pl"))
    ], self.paradigm.lemmatize("noctibus"))

  def testInflector(self):
    self.assertSameElements(["pacem"],
                            self.paradigm.inflect(
                                "pax",
                                features.FeatureVector(self.paradigm.category,
                                                       "case=acc", "num=sg")))
    self.assertSameElements(["noctibus"],
                            self.paradigm.inflect(
                                "nox",
                                features.FeatureVector(self.paradigm.category,
                                                       "case=dat", "num=pl")))


class LatinThirdDeclensionNounStemIdsTest(absltest.TestCase):
  """Shows an example of how to use stem IDs."""
  noun: features.Category
  paradigm: paradigms.Paradigm
  delete_stem_ids: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    number = features.Feature("num", "sg", "pl")
    cls.noun = features.Category(case, number)
    cls.noun = features.Category(case, number)
    nomsg = features.FeatureVector(cls.noun, "case=nom", "num=sg")
    stem = paradigms.make_byte_star_except_boundary()
    slots = [(paradigms.suffix("+s", stem), nomsg),
             (paradigms.suffix("+is", stem),
              features.FeatureVector(cls.noun, "case=gen", "num=sg")),
             (paradigms.suffix("+ī", stem),
              features.FeatureVector(cls.noun, "case=dat", "num=sg")),
             (paradigms.suffix("+em", stem),
              features.FeatureVector(cls.noun, "case=acc", "num=sg")),
             (paradigms.suffix("+e", stem),
              features.FeatureVector(cls.noun, "case=abl", "num=sg")),
             (paradigms.suffix("+ēs", stem),
              features.FeatureVector(cls.noun, "case=nom", "num=pl")),
             (paradigms.suffix("+um", stem),
              features.FeatureVector(cls.noun, "case=gen", "num=pl")),
             (paradigms.suffix("+ibus", stem),
              features.FeatureVector(cls.noun, "case=dat", "num=pl")),
             (paradigms.suffix("+ēs", stem),
              features.FeatureVector(cls.noun, "case=acc", "num=pl")),
             (paradigms.suffix("+ibus", stem),
              features.FeatureVector(cls.noun, "case=abl", "num=pl"))]
    velar = pynini.union("c", "ct", "g")
    v = pynini.union("a", "i", "ī", "e", "ē", "u")
    # Builds way more stem IDs than we need to show that that this is efficient.
    stem_ids = paradigms.build_stem_ids(1000, 101000)
    rules = [
        # c, ct, g -> x in nominative singular. Note the spelling of "cs" as "x"
        # in Latin breaks the segmentation. One might also consider representing
        # this as "c+s".
        pynini.cdrewrite(
            pynini.cross(velar, "x") + stem_ids + pynini.cross("+s", "+"), "",
            "", cls.noun.sigma_star),
        # s -> r / V __ V.
        pynini.cdrewrite(
            pynini.cross("s", "r"), "", stem_ids + "+" + v,
            cls.noun.sigma_star),
        # s+s -> s.
        pynini.cdrewrite(
            pynini.cross("s", ""), "s" + stem_ids + "+", "",
            cls.noun.sigma_star)
    ]
    cls.paradigm = paradigms.Paradigm(
        category=cls.noun,
        slots=slots,
        lemma_feature_vector=nomsg,
        stems=["noct__1000__", "ōs__1001__", "pac__1002__", "rēg__1003__"],
        rules=rules)
    cls.delete_stem_ids = pynini.cdrewrite(
        pynutil.delete(stem_ids), "", "", cls.noun.sigma_star)

  def testGenerator(self):
    generator = (
        self.paradigm.stems_to_forms @ self.paradigm.feature_label_rewriter)
    forms = rewrite.rewrites("noct__1000__", generator)
    self.assertSameElements(
        [
            "nox__1000__+[case=nom][num=sg]",
            "noct__1000__+is[case=gen][num=sg]",
            "noct__1000__+ī[case=dat][num=sg]",
            "noct__1000__+em[case=acc][num=sg]",
            "noct__1000__+e[case=abl][num=sg]",
            "noct__1000__+ēs[case=nom][num=pl]",
            "noct__1000__+um[case=gen][num=pl]",
            "noct__1000__+ibus[case=dat][num=pl]",
            "noct__1000__+ēs[case=acc][num=pl]",  # Also -īs for /i/ stems.
            "noct__1000__+ibus[case=abl][num=pl]"
        ],
        forms)
    forms = rewrite.rewrites("rēg__1003__", generator)
    self.assertSameElements([
        "rēx__1003__+[case=nom][num=sg]", "rēg__1003__+is[case=gen][num=sg]",
        "rēg__1003__+ī[case=dat][num=sg]", "rēg__1003__+em[case=acc][num=sg]",
        "rēg__1003__+e[case=abl][num=sg]", "rēg__1003__+ēs[case=nom][num=pl]",
        "rēg__1003__+um[case=gen][num=pl]",
        "rēg__1003__+ibus[case=dat][num=pl]",
        "rēg__1003__+ēs[case=acc][num=pl]", "rēg__1003__+ibus[case=abl][num=pl]"
    ], forms)
    forms = rewrite.rewrites("ōs__1001__", generator)
    self.assertSameElements([
        "ōs__1001__+[case=nom][num=sg]", "ōr__1001__+is[case=gen][num=sg]",
        "ōr__1001__+ī[case=dat][num=sg]", "ōr__1001__+em[case=acc][num=sg]",
        "ōr__1001__+e[case=abl][num=sg]", "ōr__1001__+ēs[case=nom][num=pl]",
        "ōr__1001__+um[case=gen][num=pl]", "ōr__1001__+ibus[case=dat][num=pl]",
        "ōr__1001__+ēs[case=acc][num=pl]", "ōr__1001__+ibus[case=abl][num=pl]"
    ], forms)

  def testFindForm(self):
    filt = self.noun.sigma_star + "__1001__" + self.noun.sigma_star + "[case=acc][num=sg]"
    forms = (
        self.paradigm.stems_to_forms @ filt @ self.delete_stem_ids
        @ self.paradigm.feature_label_rewriter)
    self.assertSameElements(["ōr+em[case=acc][num=sg]"],
                            forms.optimize().paths().ostrings())
    filt = self.noun.sigma_star + "__1002__" + self.noun.sigma_star + "[case=gen][num=pl]"
    forms = (
        self.paradigm.stems_to_forms @ filt @ self.delete_stem_ids
        @ self.paradigm.feature_label_rewriter)
    self.assertSameElements(["pac+um[case=gen][num=pl]"],
                            forms.optimize().paths().ostrings())


class TagalogUmInfixationTest(absltest.TestCase):
  """Tagalog data from https://unilang.org/course.php?res=79."""
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    focus = features.Feature("focus", "none", "actor")
    verb = features.Category(focus)
    none = features.FeatureVector(verb, "focus=none")
    v = pynini.union("a", "e", "i", "o", "u")
    c = pynini.union("b", "d", "f", "g", "h", "k", "l", "ly", "k", "m", "n",
                     "ng", "ny", "p", "r", "s", "t", "ts", "w", "y", "z")
    stem = paradigms.make_byte_star_except_boundary()
    um = pynini.union(c.plus + pynutil.insert("+um+") + v + stem,
                      pynutil.insert("um+") + v + stem)
    slots = [(stem, none), (um, features.FeatureVector(verb, "focus=actor"))]
    cls.paradigm = paradigms.Paradigm(
        category=verb,
        slots=slots,
        lemma_feature_vector=none,
        stems=["bilang", "ibig", "lipad", "kopya", "punta"])

  def testGenerate(self):
    form = ("bilang" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertSameElements(["bilang[focus=none]", "b+um+ilang[focus=actor]"],
                            form.paths().ostrings())
    form = ("ibig" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertSameElements(["ibig[focus=none]", "um+ibig[focus=actor]"],
                            form.paths().ostrings())

  def testAnalyzer(self):
    self.assertSameElements(
        [("l+um+ipad",
          features.FeatureVector(self.paradigm.category, "focus=actor"))],
        self.paradigm.analyze("lumipad"))

  def testTagger(self):
    self.assertSameElements(
        [("lumipad",
          features.FeatureVector(self.paradigm.category, "focus=actor"))],
        self.paradigm.tag("lumipad"))

  def testLemmatizer(self):
    self.assertSameElements([
        ("lipad", features.FeatureVector(self.paradigm.category, "focus=actor"))
    ], self.paradigm.lemmatize("lumipad"))

  def testInflector(self):
    self.assertSameElements(["lumipad"],
                            self.paradigm.inflect(
                                "lipad",
                                features.FeatureVector(self.paradigm.category,
                                                       "focus=actor")))


class YowlumneVerbalAspectTest(absltest.TestCase):
  """Yowlumne data from Roark & Sproat, 2007:32.

  Data originally from Newman (1944) via Archangeli (1984).

  Archangeli, D. 1984. Underspecification in Yawelmani Phonology and
  Morphology. PhD Thesis, Massachusetts Institute of Technology.

  Newman, S. 1944. Yokuts Language of California. Viking Fund Publications in
  Anthropology.
  """
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    # Not clear "aspect" is exactly the right concept.
    aspect = features.Feature("aspect", "root", "dubitative", "gerundial",
                              "durative")
    verb = features.Category(aspect)
    root = features.FeatureVector(verb, "aspect=root")
    stem = paradigms.make_byte_star_except_boundary()
    # Naming these with short names for space reasons.
    vowels = ("a", "i", "o", "u")
    v = pynini.union(*vowels)
    c = pynini.union("c", "m", "h", "l", "y", "k", "ʔ", "d", "n", "w", "t")
    # First template: apply Procrustean transformation to CVCC^?.
    cvcc = (c + v + pynutil.delete(v).ques + c + pynutil.delete(v).star +
            c.ques).optimize()
    # Second template: apply Procrustean transformation to CVCVVC^?. The
    # CVCVVC^? case involves copying vowels, which is most easily achieved by
    # iterating over the vowels in the construction.
    cvcvvc = pynini.Fst()
    for v in vowels:
      cvcvvc.union(c + v + pynutil.delete(v).ques + c + pynutil.delete(v).star +
                   pynutil.insert(v + v) + c.ques)
    cvcvvc.optimize()
    slots = [(stem, root),
             (paradigms.suffix("+al", stem),
              features.FeatureVector(verb, "aspect=dubitative")),
             (paradigms.suffix("+inay", stem @ cvcc),
              features.FeatureVector(verb, "aspect=gerundial")),
             (paradigms.suffix("+ʔaa", stem @ cvcvvc),
              features.FeatureVector(verb, "aspect=durative"))]
    cls.paradigm = paradigms.Paradigm(
        category=verb,
        slots=slots,
        lemma_feature_vector=root,
        stems=["caw", "cuum", "hoyoo", "diiyl", "ʔilk", "hiwiit"])

  # In the interests of brevity we just test the basic functionality of mapping
  # from stems to forms.
  def testStems(self):
    stems_and_forms = [
        ("caw", [
            "caw+al[aspect=dubitative]", "caw+inay[aspect=gerundial]",
            "cawaa+ʔaa[aspect=durative]", "caw[aspect=root]"
        ]),
        ("cuum", [
            "cuum+al[aspect=dubitative]", "cum+inay[aspect=gerundial]",
            "cumuu+ʔaa[aspect=durative]", "cuum[aspect=root]"
        ]),
        ("diiyl", [
            "diiyl+al[aspect=dubitative]", "diyl+inay[aspect=gerundial]",
            "diyiil+ʔaa[aspect=durative]", "diiyl[aspect=root]"
        ]),
        ("hiwiit", [
            "hiwiit+al[aspect=dubitative]", "hiwt+inay[aspect=gerundial]",
            "hiwiit+ʔaa[aspect=durative]", "hiwiit[aspect=root]"
        ]),
        ("hoyoo", [
            "hoyoo+al[aspect=dubitative]", "hoy+inay[aspect=gerundial]",
            "hoyoo+ʔaa[aspect=durative]", "hoyoo[aspect=root]"
        ]),
        ("ʔilk", [
            "ʔilk+al[aspect=dubitative]", "ʔilk+inay[aspect=gerundial]",
            "ʔiliik+ʔaa[aspect=durative]", "ʔilk[aspect=root]"
        ])
    ]
    generate = (
        self.paradigm.stems_to_forms @ self.paradigm.feature_label_rewriter)
    for (stem, expected) in stems_and_forms:
      predicted = rewrite.rewrites(stem, generate)
      self.assertSameElements(expected, predicted)


class RussianHardStemMasculine(absltest.TestCase):
  """Accent A and B hard stem masculine nouns in Russian.

  This also serves as a test of paradigm inheritance.
  """
  paradigm_a: paradigms.Paradigm
  paradigm_b: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    case = features.Feature("case", "nom", "gen", "dat", "acc", "ins", "prp")
    num = features.Feature("num", "sg", "pl")
    noun = features.Category(case, num)
    stem = paradigms.make_byte_star_except_boundary()
    nomsg = features.FeatureVector(noun, "case=nom", "num=sg")
    # Accent A has stem stress.
    slots_a = [
        (stem, nomsg),
        (paradigms.suffix("+a", stem),
         features.FeatureVector(noun, "case=gen", "num=sg")),
        (paradigms.suffix("+u", stem),
         features.FeatureVector(noun, "case=dat", "num=sg")),
        (stem, features.FeatureVector(noun, "case=acc", "num=sg")),
        (paradigms.suffix("+om", stem),
         features.FeatureVector(noun, "case=ins", "num=sg")),
        (paradigms.suffix("+e", stem),
         features.FeatureVector(noun, "case=prp", "num=sg")),
        (paradigms.suffix("+y", stem),
         features.FeatureVector(noun, "case=nom", "num=pl")),
        (paradigms.suffix("+ov", stem),
         features.FeatureVector(noun, "case=gen", "num=pl")),
        (paradigms.suffix("+am", stem),
         features.FeatureVector(noun, "case=dat", "num=pl")),
        (paradigms.suffix("+y", stem),
         features.FeatureVector(noun, "case=acc", "num=pl")),
        (paradigms.suffix("+ami", stem),
         features.FeatureVector(noun, "case=ins", "num=pl")),
        (paradigms.suffix("+ax", stem),
         features.FeatureVector(noun, "case=prp", "num=pl")),
    ]
    cls.paradigm_a = paradigms.Paradigm(
        category=noun,
        name="hard stem masculine accent A",
        slots=slots_a,
        lemma_feature_vector=nomsg,
        stems=["grádus", "žurnál"],
    )
    # Accent B has stress-shift to the desinence except in the nom./acc.
    deaccentuation_map = pynini.string_map([
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ý", "y"),
    ])
    acc_v = pynini.project(deaccentuation_map, "input")
    deaccentuation = pynini.cdrewrite(deaccentuation_map, "",
                                      noun.sigma_star + acc_v,
                                      noun.sigma_star).optimize()
    slots_b = [
        (paradigms.suffix("+á", stem),
         features.FeatureVector(noun, "case=gen", "num=sg")),
        (paradigms.suffix("+ú", stem),
         features.FeatureVector(noun, "case=dat", "num=sg")),
        (paradigms.suffix("+óm", stem),
         features.FeatureVector(noun, "case=ins", "num=sg")),
        (paradigms.suffix("+é", stem),
         features.FeatureVector(noun, "case=prp", "num=sg")),
        (paradigms.suffix("+ý", stem),
         features.FeatureVector(noun, "case=nom", "num=pl")),
        (paradigms.suffix("+óv", stem),
         features.FeatureVector(noun, "case=gen", "num=pl")),
        (paradigms.suffix("+ám", stem),
         features.FeatureVector(noun, "case=dat", "num=pl")),
        (paradigms.suffix("+ý", stem),
         features.FeatureVector(noun, "case=acc", "num=pl")),
        (paradigms.suffix("+ámi", stem),
         features.FeatureVector(noun, "case=ins", "num=pl")),
        (paradigms.suffix("+áx", stem),
         features.FeatureVector(noun, "case=prp", "num=pl")),
    ]
    cls.paradigm_b = paradigms.Paradigm(
        category=noun,
        name="hard stem masculine accent B",
        slots=slots_b,
        parent_paradigm=cls.paradigm_a,
        lemma_feature_vector=nomsg,
        stems=["górb", "stól"],
        rules=[deaccentuation])

  def testGenerator(self):
    generator = (
        self.paradigm_a.stems_to_forms @ self.paradigm_a.feature_label_rewriter)
    forms = rewrite.rewrites("grádus", generator)
    self.assertSameElements([
        "grádus[case=nom][num=sg]", "grádus+a[case=gen][num=sg]",
        "grádus+u[case=dat][num=sg]", "grádus[case=acc][num=sg]",
        "grádus+om[case=ins][num=sg]", "grádus+e[case=prp][num=sg]",
        "grádus+y[case=nom][num=pl]", "grádus+ov[case=gen][num=pl]",
        "grádus+am[case=dat][num=pl]", "grádus+y[case=acc][num=pl]",
        "grádus+ami[case=ins][num=pl]", "grádus+ax[case=prp][num=pl]"
    ], forms)
    generator = (
        self.paradigm_b.stems_to_forms @ self.paradigm_b.feature_label_rewriter)
    forms = rewrite.rewrites("stól", generator)
    self.assertSameElements([
        "stól[case=nom][num=sg]", "stol+á[case=gen][num=sg]",
        "stol+ú[case=dat][num=sg]", "stól[case=acc][num=sg]",
        "stol+óm[case=ins][num=sg]", "stol+é[case=prp][num=sg]",
        "stol+óv[case=gen][num=pl]", "stol+ý[case=acc][num=pl]",
        "stol+ý[case=nom][num=pl]", "stol+ám[case=dat][num=pl]",
        "stol+ámi[case=ins][num=pl]", "stol+áx[case=prp][num=pl]"
    ], forms)

  def testAnalyzer(self):
    self.assertSameElements([("grádus+ov",
                              features.FeatureVector(self.paradigm_a.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_a.analyze("grádusov"))
    self.assertSameElements([("stol+óv",
                              features.FeatureVector(self.paradigm_b.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_b.analyze("stolóv"))

  def testTagger(self):
    self.assertSameElements([("grádusov",
                              features.FeatureVector(self.paradigm_a.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_a.tag("grádusov"))
    self.assertSameElements([("stolóv",
                              features.FeatureVector(self.paradigm_b.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_b.tag("stolóv"))

  def testLemmatizer(self):
    self.assertSameElements([("grádus",
                              features.FeatureVector(self.paradigm_a.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_a.lemmatize("grádusov"))
    self.assertSameElements([("stól",
                              features.FeatureVector(self.paradigm_b.category,
                                                     "case=gen", "num=pl"))],
                            self.paradigm_b.lemmatize("stolóv"))

  def testInflector(self):
    self.assertSameElements(["grádusov"],
                            self.paradigm_a.inflect(
                                "grádus",
                                features.FeatureVector(self.paradigm_a.category,
                                                       "case=gen", "num=pl")))
    self.assertSameElements(["stolóv"],
                            self.paradigm_b.inflect(
                                "stól",
                                features.FeatureVector(self.paradigm_b.category,
                                                       "case=gen", "num=pl")))


if __name__ == "__main__":
  absltest.main()

