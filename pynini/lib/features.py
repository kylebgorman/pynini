# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Implementation of features mirroring functionality in Thrax."""

import operator
from typing import List, Dict, Optional, Iterable

import pynini
from pynini.lib import pynutil


def _concatstar(args: Iterable[pynini.FstLike]) -> pynini.Fst:
  """Helper for repeated concatenation."""
  # TODO(kbg): This is inefficient and ugly to boot.
  it = iter(args)
  result = next(it)
  # This prevents us from returning a string, or from accidentally mutating
  # the input argument.
  result = result.copy() if isinstance(result,
                                       pynini.Fst) else pynini.acceptor(result)
  for arg in it:
    result.concat(arg)
  return result


class Error(Exception):
  """Errors specific to this module."""

  pass


class Feature:
  """Container for a Feature and its values."""

  def __init__(self,
               name: str,
               *values: str,
               default: Optional[str] = None) -> None:
    """Sets up an acceptor for the defined features.

    The acceptor accepts anything in [name=v] for v in values.

    Args:
      name: a string, the name for this feature (e.g. "gender")
      *values: one or more values (e.g. "masc", "fem", "neu")
      default: if set, is the default value for this feature, which is added to
        values if not already there.
    """
    if not values:
      Error("No values provided to Feature object")
    self._name = name
    self._values = list(values)
    self._default = default
    self._default_acceptor = None
    if self._default:
      if self._default not in self._values:
        self._values.append(self._default)
      self._default_acceptor = pynini.acceptor(f"[{name}={self._default}]")
      self._default_acceptor.optimize()
    self._acceptor = pynini.union(*(f"[{self._name}={v}]"
                                    for v in self._values))
    self._acceptor.optimize()

  def __eq__(self, other: "Feature") -> bool:
    return (isinstance(other, self.__class__) and self.name == other.name and
            frozenset(self.values) == frozenset(other.values))

  def __ne__(self, other: "Feature") -> bool:
    return not self.__eq__(other)

  @property
  def name(self) -> str:
    return self._name

  @property
  def values(self) -> List[str]:
    return self._values

  @property
  def acceptor(self) -> pynini.Fst:
    return self._acceptor

  @property
  def default_acceptor(self) -> Optional[pynini.Fst]:
    return self._default_acceptor


class Category:
  """Container for a Category and its features."""

  def __init__(self, *features: Feature) -> None:
    """Sets up an acceptor for the defined category.

    The acceptor will accept a sequence valid values for each feature, where
    the ordering is given by the lexicographic order of the name of the
    features --- i.e. the order in which they are given to the constructor is
    irrelevant.

    If one has previously defined:

        case = Feature("case", "nom", "acc", "gen", "dat")
        gen = Feature("gen", "mas", "fem", "neu")
        num = Feature("num", "sg", "pl")

    Then

        noun = Category(case, gen, num)

    will allow any sequence in

        ([case=nom] | [case=nom] | [case=acc] | [case=gen] | [case=dat]) +
        ([gen=mas] | [gen=fem] | [gen=neu]) +
        ([num=sg] | [num=pl])

    The feature_filler fills in missing feature values with either the default
    for the given feature if there is one, otherwise all possible values. So if
    we have

        case: nom, gen, acc, n/a
        num: sg, pl

    where "n/a" is the default feature (specified with the default keyword to
    the Feature), then

        [num=sg]

    will be filled to

        [case=n/a][num=sg]

    but

        [case=gen]

    will be filled to

        [case=gen]([num=sg]|[num=pl])

    Args:
      *features: one or more Features.
    """
    if not features:
      Error("No features provided to Category object")
    self._features = sorted(features, key=operator.attrgetter("name"))
    self._acceptor = _concatstar(f.acceptor for f in self._features).rmepsilon()
    self._feature_mapper = self._make_feature_mapper()
    transducers = []
    for f in self._features:
      default = f.default_acceptor if f.default_acceptor else f.acceptor
      transducers.append(pynutil.insert(default) | f.acceptor)
    self._feature_filler = _concatstar(transducers).optimize()

  def __eq__(self, other: "Category") -> bool:
    return (isinstance(other, self.__class__) and
            self.features == other.features)

  def __ne__(self, other: "Category") -> bool:
    return not self.__eq__(other)

  @property
  def features(self) -> List[Feature]:
    return self._features

  @property
  def acceptor(self) -> pynini.Fst:
    return self._acceptor

  @property
  def feature_filler(self) -> pynini.Fst:
    return self._feature_filler

  @property
  def feature_mapper(self) -> pynini.Fst:
    return self._feature_mapper

  def _make_feature_mapper(self) -> pynini.Fst:
    r"""Convenience func to map from internal syms to human-readable strings.

    Returns:
      A transducer that maps from internal symbols like "[case=nom]" to a
      sequence that will be readable as a string ("\[case=nom\]") for all
      feature-value combinations.
    """
    pairs = []
    for feature in self._features:
      name = feature.name
      for value in feature.values:
        f = f"[{name}={value}]"
        v = pynini.escape(f"[{name}={value}]")
        pairs.append(pynini.cross(f, v))
    return pynini.union(*pairs).closure().optimize()


class FeatureVector:
  """Container of category and feature settings."""

  def __init__(self, category: Category, *features_and_values: str) -> None:
    """Sets up an acceptor for the defined category.

    Args:
      category: a Category.
      *features_and_values: list of strings, consisting of specific
        feature-value settings such as "num=sg", "gen=mas", etc.

    Raises:
       Error: No features_and_values provided.
       Error: Invalid name.
    """
    if not features_and_values:
      raise Error("No features_and_values provided")
    self._category = category
    self._feature_settings = {}
    valid_names = frozenset(f.name for f in category.features)
    for feature_and_value in features_and_values:
      (f, v) = feature_and_value.split("=")
      if f not in valid_names:
        raise Error(f"Invalid name: {f}")
      self._feature_settings[f] = v
    acceptors = []
    for feature in category.features:
      if feature.name in self._feature_settings:
        if self._feature_settings[feature.name] not in feature.values:
          raise Error(f"Invalid name: {feature.name}")
        acceptors.append(
            f"[{feature.name}={self._feature_settings[feature.name]}]")
      else:
        # If not specified, allows all values.
        acceptors.append(feature.acceptor)
    self._acceptor = _concatstar(acceptors).rmepsilon()

  def __eq__(self, other: "FeatureVector") -> bool:
    return (isinstance(other, self.__class__) and
            self.category == other.category and
            self.feature_settings == other.feature_settings)

  def __ne__(self, other: "FeatureVector") -> bool:
    return not self.__eq__(other)

  def unify(self, other: "FeatureVector") -> Optional["FeatureVector"]:
    """Implements (non-reentrant) unification.

    Args:
      other: a FeatureVector.

    Returns:
      A FeatureVector representing the unification of the two FeatureVectors, or
      None if of different categories or if there is a feature-value mismatch.
    """
    if self.category != other.category:
      return None
    feature_settings = set()
    for f in self.feature_settings:
      v = self.feature_settings[f]
      if f in other.feature_settings:
        if other.feature_settings[f] != v:  # Mismatch failure.
          return None
        else:
          feature_settings.add(f"{f}={v}")
      else:
        feature_settings.add(f"{f}={v}")
    for f in other.feature_settings:
      v = other.feature_settings[f]
      if f in self.feature_settings:
        if self.feature_settings[f] != v:  # Mismatch failure.
          return None
        else:
          feature_settings.add(f"{f}={v}")
      else:
        feature_settings.add(f"{f}={v}")
    return FeatureVector(self.category, *feature_settings)

  @property
  def acceptor(self) -> pynini.Fst:
    return self._acceptor

  @property
  def category(self) -> Category:
    return self._category

  @property
  def feature_settings(self) -> Dict[str, str]:
    return self._feature_settings

