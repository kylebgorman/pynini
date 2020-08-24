# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests for Features, Categories and FeatureVectors."""

import unittest

import pynini
from pynini.lib import features


class FeaturesTest(unittest.TestCase):
  case: features.Feature
  number: features.Feature
  gender: features.Feature
  noun: features.Category
  fm: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super(FeaturesTest, cls).setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc")
    cls.number = features.Feature("num", "sg", "pl")
    cls.gender = features.Feature("gen", "mas", "fem", "neu")
    cls.noun = features.Category(cls.case, cls.number, cls.gender)
    cls.fm = cls.noun.feature_mapper

  def testFeature(self):
    self.assertEqual(self.case.name, "case")
    self.assertCountEqual(self.case.values, ("nom", "gen", "dat", "acc"))
    golden_acceptor = pynini.union("[case=nom]", "[case=gen]", "[case=dat]",
                                   "[case=acc]").optimize()
    self.assertEqual(self.case.acceptor, golden_acceptor)

  def testCategory(self):
    cat = "[case=nom][gen=fem][num=sg]" @ self.noun.acceptor @ self.fm
    self.assertEqual(cat.string(), "[case=nom][gen=fem][num=sg]")
    # Wrong order won't work.
    cat = "[case=nom][num=sg][gen=fem]" @ self.noun.acceptor @ self.fm
    self.assertEqual(cat.start(), pynini.NO_STATE_ID)

  def testCategoryEquality(self):
    case = features.Feature("case", "gen", "nom", "acc", "dat")
    number = features.Feature("num", "pl", "sg")
    gender = features.Feature("gen", "fem", "mas", "neu")
    noun = features.Category(case, number, gender)
    self.assertEqual(noun, self.noun)

  def testFeatureVector(self):
    fv = features.FeatureVector(self.noun, "num=sg", "case=dat")
    fvm = fv.acceptor @ self.fm
    self.assertCountEqual(
        fvm.paths().ostrings(),
        ("[case=dat][gen=fem][num=sg]", "[case=dat][gen=mas][num=sg]",
         "[case=dat][gen=neu][num=sg]"))
    fv = features.FeatureVector(self.noun, "gen=fem", "case=nom")
    fvm = fv.acceptor @ self.fm
    self.assertCountEqual(fvm.paths().ostrings(), (
        "[case=nom][gen=fem][num=sg]",
        "[case=nom][gen=fem][num=pl]",
    ))
    # Checks that we fail appropriately when we pass an illegal combo.
    with self.assertRaises(features.Error):
      fv = features.FeatureVector(self.noun, "gen=acc", "case=nom")
    with self.assertRaises(features.Error):
      fv = features.FeatureVector(self.noun, "gen=foofoo", "case=nom")
    with self.assertRaises(features.Error):
      fv = features.FeatureVector(self.noun, "wiggywoggy=fem", "case=nom")

  def testUnification(self):
    fv = features.FeatureVector(self.noun, "num=sg", "case=dat")
    fv_other = features.FeatureVector(self.noun, "num=sg", "case=dat")
    # Identical should unify to the same.
    self.assertEqual(fv.unify(fv_other), fv)
    # Feature clash should fail.
    fv_other = features.FeatureVector(self.noun, "num=sg", "case=nom")
    self.assertFalse(fv.unify(fv_other))
    fv_orig = fv
    fv = features.FeatureVector(self.noun, "num=sg")
    fv_other = features.FeatureVector(self.noun, "case=dat")
    # Free values for features unify with any particular specification.
    self.assertEqual(fv.unify(fv_other), fv_orig)
    some_other_category = features.Category(self.number, self.gender)
    # Mismatched categories should fail.
    fv_other = features.FeatureVector(some_other_category, "num=sg")
    self.assertFalse(fv.unify(fv_other))


class FeatureFillerTest(unittest.TestCase):
  case: features.Feature
  number: features.Feature
  gender: features.Feature
  noun: features.Category
  fm: pynini.Fst

  @classmethod
  def setUpClass(cls):
    super(FeatureFillerTest, cls).setUpClass()
    cls.case = features.Feature("case", "nom", "gen", "dat", "acc")
    cls.number = features.Feature("num", "sg", "pl")
    cls.gender = features.Feature("gen", "mas", "fem", "neu", default="n/a")
    cls.noun = features.Category(cls.case, cls.number, cls.gender)
    cls.fm = cls.noun.feature_mapper

  def testFeatureFiller(self):
    cat = "[case=nom][gen=fem][num=sg]" @ self.noun.feature_filler @ self.fm
    self.assertEqual(cat.string(), "[case=nom][gen=fem][num=sg]")
    # n/a is defined as the default feature for gender so if that is not
    # specified it gets filled in as n/a:
    cat = "[case=nom][num=sg]" @ self.noun.feature_filler @ self.fm
    self.assertEqual(cat.string(), "[case=nom][gen=n/a][num=sg]")
    # number has no default so we get all values:
    cat = "[case=nom][gen=mas]" @ self.noun.feature_filler @ self.fm
    self.assertCountEqual(
        cat.paths().ostrings(),
        ["[case=nom][gen=mas][num=sg]", "[case=nom][gen=mas][num=pl]"])
    # If we specify nothing we get all values for case and number, and n/a for
    # gender:
    cat = "" @ self.noun.feature_filler @ self.fm
    self.assertCountEqual(cat.paths().ostrings(), [
        "[case=nom][gen=n/a][num=sg]", "[case=nom][gen=n/a][num=pl]",
        "[case=gen][gen=n/a][num=sg]", "[case=gen][gen=n/a][num=pl]",
        "[case=dat][gen=n/a][num=sg]", "[case=dat][gen=n/a][num=pl]",
        "[case=acc][gen=n/a][num=sg]", "[case=acc][gen=n/a][num=pl]"
    ])


if __name__ == "__main__":
  unittest.main()

