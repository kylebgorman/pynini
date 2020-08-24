# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests for Paradigms."""

from typing import List

import unittest

import pynini
from pynini.lib import byte
from pynini.lib import features
from pynini.lib import paradigms
from pynini.lib import pynutil


class ParadigmsTestFirstDeclension(unittest.TestCase):
  case: features.Feature
  number: features.Feature
  noun: features.Category
  slots: List[paradigms.ParadigmSlot]
  steps: List[str]
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    cls.number = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    cls.noun = features.Category(cls.case, cls.number)
    stem = paradigms.make_byte_star_except_boundary("+")
    cls.slots = [(paradigms.suffix("+a", stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=sg")),
                 (paradigms.suffix("+am", stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=sg")),
                 (paradigms.suffix("+ā", stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=pl")),
                 (paradigms.suffix("+ārum", stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=pl")),
                 (paradigms.suffix("+īs", stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=pl")),
                 (paradigms.suffix("+ās", stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=pl")),
                 (paradigms.suffix("+īs", stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=pl"))]
    cls.stems = ("aqu", "bell", "caus", "cicād", "mens", "naut", "puell")
    cls.paradigm = paradigms.Paradigm(
        category=cls.noun,
        name="Declension I",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.noun, "case=nom",
                                                    "num=sg"))
    cls.paradigm.set_stems_to_forms(cls.stems)

  def testSetStemToForms(self):
    form = ("aqu" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "aqu+a[case=nom][num=sg]", "aqu+ae[case=gen][num=sg]",
        "aqu+ae[case=dat][num=sg]", "aqu+am[case=acc][num=sg]",
        "aqu+ā[case=abl][num=sg]", "aqu+ae[case=nom][num=pl]",
        "aqu+ārum[case=gen][num=pl]", "aqu+īs[case=dat][num=pl]",
        "aqu+ās[case=acc][num=pl]", "aqu+īs[case=abl][num=pl]"
    ],
                            form.paths().ostrings())

  def testAnalyzer(self):
    form = ("aquārum" @ self.paradigm.analyzer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["aqu+ārum[case=gen][num=pl]"],
                            form.paths().ostrings())
    form = ("puellīs" @ self.paradigm.analyzer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(
        ("puell+īs[case=dat][num=pl]", "puell+īs[case=abl][num=pl]"),
        form.paths().ostrings())

  def testTagger(self):
    form = (
        "aquārum" @ self.paradigm.tagger @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["aquārum[case=gen][num=pl]"],
                            form.paths().ostrings())
    form = (
        "puellīs" @ self.paradigm.tagger @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(
        ["puellīs[case=dat][num=pl]", "puellīs[case=abl][num=pl]"],
        form.paths().ostrings())

  def testLemmatizer(self):
    form = ("aquārum" @ self.paradigm.lemmatizer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["aqua[case=gen][num=pl]"], form.paths().ostrings())
    form = ("puellīs" @ self.paradigm.lemmatizer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(
        ["puella[case=dat][num=pl]", "puella[case=abl][num=pl]"],
        form.paths().ostrings())

  def testInflector(self):
    form = "aqua[case=gen][num=pl]" @ self.paradigm.inflector
    self.assertCountEqual(["aquārum"], form.paths().ostrings())
    form = "puella[case=dat][num=pl]" @ self.paradigm.inflector
    self.assertCountEqual(["puellīs"], form.paths().ostrings())


class ParadigmsTestThirdDeclension(unittest.TestCase):
  """Or more specifically a few 3rd declension consonant-final stems."""
  case: features.Feature
  number: features.Feature
  noun: features.Category
  stem: pynini.Fst
  slots: List[paradigms.ParadigmSlot]
  stems: List[str]
  sigma: pynini.Fst
  vowels: pynini.Fst
  paradigm: paradigms.Paradigm
  rules: List[pynini.Fst]

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    cls.number = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    cls.noun = features.Category(cls.case, cls.number)
    cls.stem = paradigms.make_byte_star_except_boundary("+")
    cls.slots = [(paradigms.suffix("+s", cls.stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=sg")),
                 (paradigms.suffix("+is", cls.stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=sg")),
                 (paradigms.suffix("+ī", cls.stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=sg")),
                 (paradigms.suffix("+em", cls.stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=sg")),
                 (paradigms.suffix("+e", cls.stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=sg")),
                 (paradigms.suffix("+ēs", cls.stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=pl")),
                 (paradigms.suffix("+um", cls.stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=pl")),
                 (paradigms.suffix("+ibus", cls.stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=pl")),
                 (paradigms.suffix("+ēs", cls.stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=pl")),
                 (paradigms.suffix("+ibus", cls.stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=pl"))]
    cls.stems = ("noct", "ōs", "pac", "rēg")
    cls.sigma = (pynini.project(cls.noun.feature_mapper, "input")
                 | byte.BYTES).closure()
    velars = pynini.union("c", "ct", "g")
    cls.vowels = pynini.union("a", "i", "ī", "e", "ē", "u")
    cls.rules = [
        # c, ct, g -> x in nominative singular. Note the spelling of "cs" as "x"
        # in Latin breaks the segmentation. One might also consider representing
        # this as "c+s".
        pynini.cdrewrite(pynini.cross(velars + "+s", "x+"), "", "", cls.sigma),
        # Rhotacize /s/ prevocalically: a non-Gorman theory of this alternation.
        pynini.cdrewrite(
            pynini.cross("s", "r"), "", "+" + cls.vowels, cls.sigma),
        # s+s -> s.
        pynini.cdrewrite(pynini.cross("s+s", "s+"), "", "", cls.sigma)
    ]
    cls.paradigm = paradigms.Paradigm(
        category=cls.noun,
        name="Declension III",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.noun, "case=nom",
                                                    "num=sg"),
        rules=cls.rules)
    cls.paradigm.set_stems_to_forms(cls.stems)

  def testSetStemToForms(self):
    form = ("noct" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(
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
        form.paths().ostrings())
    form = ("rēg" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "rēx+[case=nom][num=sg]", "rēg+is[case=gen][num=sg]",
        "rēg+ī[case=dat][num=sg]", "rēg+em[case=acc][num=sg]",
        "rēg+e[case=abl][num=sg]", "rēg+ēs[case=nom][num=pl]",
        "rēg+um[case=gen][num=pl]", "rēg+ibus[case=dat][num=pl]",
        "rēg+ēs[case=acc][num=pl]", "rēg+ibus[case=abl][num=pl]"
    ],
                            form.paths().ostrings())
    form = ("ōs" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "ōs+[case=nom][num=sg]", "ōr+is[case=gen][num=sg]",
        "ōr+ī[case=dat][num=sg]", "ōr+em[case=acc][num=sg]",
        "ōr+e[case=abl][num=sg]", "ōr+ēs[case=nom][num=pl]",
        "ōr+um[case=gen][num=pl]", "ōr+ibus[case=dat][num=pl]",
        "ōr+ēs[case=acc][num=pl]", "ōr+ibus[case=abl][num=pl]"
    ],
                            form.paths().ostrings())

  def testAnalyzer(self):
    form = (
        "ōs" @ self.paradigm.analyzer @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["ōs+[case=nom][num=sg]"], form.paths().ostrings())
    form = (
        "rēge" @ self.paradigm.analyzer @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["rēg+e[case=abl][num=sg]"],
                            form.paths().ostrings())

  def testTagger(self):
    form = ("ōs" @ self.paradigm.tagger @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["ōs[case=nom][num=sg]"], form.paths().ostrings())
    form = (
        "rēge" @ self.paradigm.tagger @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["rēge[case=abl][num=sg]"], form.paths().ostrings())

  def testLemmatizer(self):
    form = ("pacem" @ self.paradigm.lemmatizer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["pax[case=acc][num=sg]"], form.paths().ostrings())
    form = ("noctibus" @ self.paradigm.lemmatizer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["nox[case=dat][num=pl]", "nox[case=abl][num=pl]"],
                            form.paths().ostrings())

  def testInflector(self):
    form = "pax[case=acc][num=sg]" @ self.paradigm.inflector
    self.assertCountEqual(["pacem"], form.paths().ostrings())
    form = "nox[case=dat][num=pl]" @ self.paradigm.inflector
    self.assertCountEqual(["noctibus"], form.paths().ostrings())

  def testInheritance(self):
    # Not necessarily the best way to handle neuter third declension nouns, but
    # just for illustrative purposes.
    slots = [(paradigms.suffix("+", self.stem),
              features.FeatureVector(self.noun, "case=nom", "num=sg")),
             (paradigms.suffix("+", self.stem),
              features.FeatureVector(self.noun, "case=acc", "num=sg")),
             (paradigms.suffix("+a", self.stem),
              features.FeatureVector(self.noun, "case=nom", "num=pl")),
             (paradigms.suffix("+a", self.stem),
              features.FeatureVector(self.noun, "case=acc", "num=pl"))]
    only_features = pynini.project(self.noun.feature_mapper, "input")
    new_rules = [
        # Deletes final "t" in "lact".
        pynini.cdrewrite(
            pynini.cross("t", ""), "c", "+" + only_features + "[EOS]",
            self.sigma),
        # Stem alternation in "tempus"/"tempor"; /r/ is already taken care of.
        pynini.cdrewrite(
            pynini.cross("ur", "or"), "", "+" + self.vowels, self.sigma)
    ]
    neuter_third = paradigms.Paradigm(
        category=self.noun,
        name="Declension III Neuter",
        slots=slots,
        lemma_feature_vector=features.FeatureVector(self.noun, "case=nom",
                                                    "num=sg"),
        rules=self.rules + new_rules,
        parent_paradigm=self.paradigm)
    stems = ["lact", "tempus"]  # lac doesn't really have a plural...
    neuter_third.set_stems_to_forms(stems)
    form = ("lac" @ neuter_third.tagger @ neuter_third.feature_label_rewriter)
    self.assertCountEqual(["lac[case=nom][num=sg]", "lac[case=acc][num=sg]"],
                            form.paths().ostrings())
    form = ("lactibus" @ neuter_third.lemmatizer
            @ neuter_third.feature_label_rewriter)
    self.assertCountEqual(["lac[case=abl][num=pl]", "lac[case=dat][num=pl]"],
                            form.paths().ostrings())
    form = ("temporibus" @ neuter_third.lemmatizer
            @ neuter_third.feature_label_rewriter)
    self.assertCountEqual(
        ["tempus[case=abl][num=pl]", "tempus[case=dat][num=pl]"],
        form.paths().ostrings())
    form = ("tempora" @ neuter_third.lemmatizer
            @ neuter_third.feature_label_rewriter)
    self.assertCountEqual(
        ["tempus[case=acc][num=pl]", "tempus[case=nom][num=pl]"],
        form.paths().ostrings())
    form = "tempus[case=acc][num=pl]" @ neuter_third.inflector
    self.assertCountEqual(("tempora",), form.paths().ostrings())


class ParadigmsTestInfix(unittest.TestCase):
  """Tagalog data from https://unilang.org/course.php?res=79."""
  finite: features.Feature
  verb: features.Category
  slots: List[paradigms.ParadigmSlot]
  stems: List[str]
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.finite = features.Feature("finite", "+", "-")
    cls.verb = features.Category(cls.finite)
    consonant = pynini.union("k", "b", "g", "r")
    vowel = pynini.union("a", "i")
    stem = paradigms.make_byte_star_except_boundary("+")
    um_infixation = ((pynini.closure(consonant, 1) + pynutil.insert("+um+") +
                      vowel + stem) | (pynutil.insert("um+") + vowel + stem))
    cls.slots = [(stem, features.FeatureVector(cls.verb, "finite=+")),
                 (um_infixation, features.FeatureVector(cls.verb, "finite=-"))]
    cls.stems = ["alis", " kain", "bili", "inom", "gawa", "graduet"]
    cls.paradigm = paradigms.Paradigm(
        category=cls.verb,
        name="Finiteness",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.verb, "finite=+"))
    cls.paradigm.set_stems_to_forms(cls.stems)

  def testSetStemToForms(self):
    form = ("alis" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["alis[finite=+]", "um+alis[finite=-]"],
                            form.paths().ostrings())
    form = ("bili" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["bili[finite=+]", "b+um+ili[finite=-]"],
                            form.paths().ostrings())
    form = ("graduet" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["graduet[finite=+]", "gr+um+aduet[finite=-]"],
                            form.paths().ostrings())

  def testAnalyzer(self):
    form = ("grumaduet" @ self.paradigm.analyzer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["gr+um+aduet[finite=-]"], form.paths().ostrings())

  def testTagger(self):
    form = ("grumaduet" @ self.paradigm.tagger
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["grumaduet[finite=-]"], form.paths().ostrings())

  def testLemmatizer(self):
    form = ("grumaduet" @ self.paradigm.lemmatizer
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["graduet[finite=-]"], form.paths().ostrings())

  def testInflector(self):
    form = "graduet[finite=-]" @ self.paradigm.inflector
    self.assertCountEqual(["grumaduet"], form.paths().ostrings())


class ParadigmsTestTemplaticMorphology(unittest.TestCase):
  """Yowlumne data from Roark & Sproat, 2007, p.

  32.

  Data originally from Newman (1944) via Archangeli (1984).

  Archangeli, D. 1984. Underspecification in Yawelmani Phonology and
  Morphology. PhD Thesis, MIT.

  Newman, S. 1944. Yokuts Language of California. Viking Fund Publications in
  Anthropology. New York.
  """
  aspect: features.Feature
  verb: features.Category
  stems: List[str]
  slots: List[paradigms.ParadigmSlot]
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    # Not clear "aspect" is exactly the right concept.
    cls.aspect = features.Feature("aspect", "root", "dubitative", "gerundial",
                                  "durative")
    cls.verb = features.Category(cls.aspect)
    stem = paradigms.make_byte_star_except_boundary("+")
    # Naming these with short names for space reasons.
    vowels = ("a", "i", "o", "u")
    v = pynini.union(*vowels)
    c = pynini.union("c", "m", "h", "l", "y", "k", "ʔ", "d", "n", "w", "t")
    # First template: apply Procrustean transformation to CVCC?
    cvcc = (c + v + pynutil.delete(v).ques + c + pynutil.delete(v).star +
            c.ques).optimize()
    # Second template: apply Procrustean transformation to CVCVVC?.  The CVCVVC?
    # case involves copying vowels, which is most easily achieved by iterating
    # over the vowels in the construction.
    cvcvvc = pynini.cross("", "")
    for vo in vowels:
      cvcvvc |= (
          c + vo + pynutil.delete(vo).ques + c + pynutil.delete(vo).star +
          pynutil.insert(vo + vo) + c.ques)
    cvcvvc.optimize()
    cls.stems = ("caw", "cuum", "hoyoo", "diiyl", "ʔilk", "hiwiit")
    cls.slots = [(stem, features.FeatureVector(cls.verb, "aspect=root")),
                 (paradigms.suffix("+al", stem),
                  features.FeatureVector(cls.verb, "aspect=dubitative")),
                 (paradigms.suffix("+inay", stem @ cvcc),
                  features.FeatureVector(cls.verb, "aspect=gerundial")),
                 (paradigms.suffix("+ʔaa", stem @ cvcvvc),
                  features.FeatureVector(cls.verb, "aspect=durative"))]
    cls.paradigm = paradigms.Paradigm(
        category=cls.verb,
        name="Yowlumne Verb Forms",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.verb, "aspect=root"))
    cls.paradigm.set_stems_to_forms(cls.stems)

  # In the interests of brevity we just test the basic functionality of mapping
  # from stems to forms.
  def testSetStemToForms(self):
    stems_and_forms = [
        ("caw", ("caw+al[aspect=dubitative]", "caw+inay[aspect=gerundial]",
                 "cawaa+ʔaa[aspect=durative]", "caw[aspect=root]")),
        ("cuum", ("cuum+al[aspect=dubitative]", "cum+inay[aspect=gerundial]",
                  "cumuu+ʔaa[aspect=durative]", "cuum[aspect=root]")),
        ("diiyl", ("diiyl+al[aspect=dubitative]", "diyl+inay[aspect=gerundial]",
                   "diyiil+ʔaa[aspect=durative]", "diiyl[aspect=root]")),
        ("hiwiit",
         ("hiwiit+al[aspect=dubitative]", "hiwt+inay[aspect=gerundial]",
          "hiwiit+ʔaa[aspect=durative]", "hiwiit[aspect=root]")),
        ("hoyoo", ("hoyoo+al[aspect=dubitative]", "hoy+inay[aspect=gerundial]",
                   "hoyoo+ʔaa[aspect=durative]", "hoyoo[aspect=root]")),
        ("ʔilk", ("ʔilk+al[aspect=dubitative]", "ʔilk+inay[aspect=gerundial]",
                  "ʔiliik+ʔaa[aspect=durative]", "ʔilk[aspect=root]"))
    ]
    for (stem, forms) in stems_and_forms:
      stem = (
          stem @ self.paradigm.stems_to_forms
          @ self.paradigm.feature_label_rewriter)
      self.assertCountEqual(forms, stem.paths().ostrings())


class ParadigmsTestWildCardStem(unittest.TestCase):
  """Uses Latin first declension again to test an acceptor as a stem."""
  case: features.Feature
  number: features.Feature
  noun: features.Feature
  slots: List[paradigms.ParadigmSlot]
  stems: List[pynini.Fst]
  paradigm: paradigms.Paradigm

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    cls.number = features.Feature("num", "sg", "pl")
    # Ignoring gender since gender is a property of the stem rather than the
    # ending.
    cls.noun = features.Category(cls.case, cls.number)
    stem = paradigms.make_byte_star_except_boundary("+")
    cls.slots = [(paradigms.suffix("+a", stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=sg")),
                 (paradigms.suffix("+am", stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=sg")),
                 (paradigms.suffix("+ā", stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=sg")),
                 (paradigms.suffix("+ae", stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=pl")),
                 (paradigms.suffix("+ārum", stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=pl")),
                 (paradigms.suffix("+īs", stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=pl")),
                 (paradigms.suffix("+ās", stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=pl")),
                 (paradigms.suffix("+īs", stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=pl"))]
    v = pynini.union("a", "i", "e", "o", "u")
    c = pynini.union("b", "c", "d", "f", "g", "h", "l", "m", "n", "p", "q", "r",
                     "s", "t")
    cls.stems = [(v | c).closure(1)]
    cls.paradigm = paradigms.Paradigm(
        category=cls.noun,
        name="Declension I",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.noun, "case=nom",
                                                    "num=sg"))
    cls.paradigm.set_stems_to_forms(cls.stems)

  def testSetStemToForms(self):
    form = ("aqu" @ self.paradigm.stems_to_forms
            @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "aqu+a[case=nom][num=sg]", "aqu+ae[case=gen][num=sg]",
        "aqu+ae[case=dat][num=sg]", "aqu+am[case=acc][num=sg]",
        "aqu+ā[case=abl][num=sg]", "aqu+ae[case=nom][num=pl]",
        "aqu+ārum[case=gen][num=pl]", "aqu+īs[case=dat][num=pl]",
        "aqu+ās[case=acc][num=pl]", "aqu+īs[case=abl][num=pl]"
    ],
                            form.paths().ostrings())


class ParadigmsTestThirdDeclensionWithStemIds(unittest.TestCase):
  """Or more specifically a few 3rd declension consonant-final stems.

  Shows an example of how to use stem IDs.
  """
  case: features.Feature
  number: features.Feature
  noun: features.Category
  stem: pynini.Fst
  slots: List[paradigms.ParadigmSlot]
  sigma: pynini.Fst
  rules: List[pynini.Fst]
  paradigm: paradigms.Paradigm
  delete_stem_ids: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc", "abl")
    cls.number = features.Feature("num", "sg", "pl")
    cls.noun = features.Category(cls.case, cls.number)
    cls.stem = paradigms.make_byte_star_except_boundary("+")
    cls.slots = [(paradigms.suffix("+s", cls.stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=sg")),
                 (paradigms.suffix("+is", cls.stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=sg")),
                 (paradigms.suffix("+ī", cls.stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=sg")),
                 (paradigms.suffix("+em", cls.stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=sg")),
                 (paradigms.suffix("+e", cls.stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=sg")),
                 (paradigms.suffix("+ēs", cls.stem),
                  features.FeatureVector(cls.noun, "case=nom", "num=pl")),
                 (paradigms.suffix("+um", cls.stem),
                  features.FeatureVector(cls.noun, "case=gen", "num=pl")),
                 (paradigms.suffix("+ibus", cls.stem),
                  features.FeatureVector(cls.noun, "case=dat", "num=pl")),
                 (paradigms.suffix("+ēs", cls.stem),
                  features.FeatureVector(cls.noun, "case=acc", "num=pl")),
                 (paradigms.suffix("+ibus", cls.stem),
                  features.FeatureVector(cls.noun, "case=abl", "num=pl"))]
    stems = ["noct__1000__", "ōs__1001__", "pac__1002__", "rēg__1003__"]
    velars = pynini.union("c", "ct", "g")
    vowels = pynini.union("a", "i", "ī", "e", "ē", "u")
    cls.sigma = pynini.project(cls.noun.feature_mapper, "input") | byte.BYTES
    cls.sigma.closure()
    # Builds way more stem IDs than we need to show that that this is efficient.
    stem_ids = paradigms.build_stem_ids(1000, 101000)
    cls.rules = [
        # c, ct, g -> x in nominative singular. Note the spelling of "cs" as "x"
        # in Latin breaks the segmentation. One might also consider representing
        # this as "c+s".
        pynini.cdrewrite(
            pynini.cross(velars, "x") + stem_ids + pynini.cross("+s", "+"), "",
            "", cls.sigma),
        # s -> r intervocalically.
        pynini.cdrewrite(
            pynini.cross("s", "r"), "", stem_ids + "+" + vowels, cls.sigma),
        # s -> r intervocalically.
        pynini.cdrewrite(
            pynini.cross("s", "r"), "", stem_ids + "+" + vowels, cls.sigma),
        pynini.cdrewrite(
            pynini.cross("s", ""), "s" + stem_ids + "+", "", cls.sigma)
    ]
    cls.paradigm = paradigms.Paradigm(
        category=cls.noun,
        name="Declension III",
        slots=cls.slots,
        lemma_feature_vector=features.FeatureVector(cls.noun, "case=nom",
                                                    "num=sg"),
        rules=cls.rules)
    cls.paradigm.set_stems_to_forms(stems)
    cls.delete_stem_ids = pynini.cdrewrite(
        pynini.cross(stem_ids, ""), "", "", cls.sigma)

  def testSetStemToForms(self):
    forms = ("noct__1000__" @ self.paradigm.stems_to_forms
             @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(
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
        forms.paths().ostrings())
    forms = ("rēg__1003__" @ self.paradigm.stems_to_forms
             @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "rēx__1003__+[case=nom][num=sg]", "rēg__1003__+is[case=gen][num=sg]",
        "rēg__1003__+ī[case=dat][num=sg]", "rēg__1003__+em[case=acc][num=sg]",
        "rēg__1003__+e[case=abl][num=sg]", "rēg__1003__+ēs[case=nom][num=pl]",
        "rēg__1003__+um[case=gen][num=pl]",
        "rēg__1003__+ibus[case=dat][num=pl]",
        "rēg__1003__+ēs[case=acc][num=pl]", "rēg__1003__+ibus[case=abl][num=pl]"
    ],
                            forms.paths().ostrings())
    forms = ("ōs__1001__" @ self.paradigm.stems_to_forms
             @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "ōs__1001__+[case=nom][num=sg]", "ōr__1001__+is[case=gen][num=sg]",
        "ōr__1001__+ī[case=dat][num=sg]", "ōr__1001__+em[case=acc][num=sg]",
        "ōr__1001__+e[case=abl][num=sg]", "ōr__1001__+ēs[case=nom][num=pl]",
        "ōr__1001__+um[case=gen][num=pl]", "ōr__1001__+ibus[case=dat][num=pl]",
        "ōr__1001__+ēs[case=acc][num=pl]", "ōr__1001__+ibus[case=abl][num=pl]"
    ],
                            forms.paths().ostrings())
    forms = ("ōs__1001__" @ self.paradigm.stems_to_forms @ self.delete_stem_ids
             @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual([
        "ōs+[case=nom][num=sg]", "ōr+is[case=gen][num=sg]",
        "ōr+ī[case=dat][num=sg]", "ōr+em[case=acc][num=sg]",
        "ōr+e[case=abl][num=sg]", "ōr+ēs[case=nom][num=pl]",
        "ōr+um[case=gen][num=pl]", "ōr+ibus[case=dat][num=pl]",
        "ōr+ēs[case=acc][num=pl]", "ōr+ibus[case=abl][num=pl]"
    ],
                            forms.optimize().paths().ostrings())

  def testFindForm(self):
    filt = self.sigma + "__1001__" + self.sigma + "[case=acc][num=sg]"
    forms = (
        self.paradigm.stems_to_forms @ filt @ self.delete_stem_ids
        @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["ōr+em[case=acc][num=sg]"],
                            forms.optimize().paths().ostrings())
    filt = self.sigma + "__1002__" + self.sigma + "[case=gen][num=pl]"
    forms = (
        self.paradigm.stems_to_forms @ filt @ self.delete_stem_ids
        @ self.paradigm.feature_label_rewriter)
    self.assertCountEqual(["pac+um[case=gen][num=pl]"],
                            forms.optimize().paths().ostrings())


if __name__ == "__main__":
  unittest.main()

