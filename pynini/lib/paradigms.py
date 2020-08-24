# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Implementation of paradigms, mirroring and extending functionality in Thrax.

This follows the treatment of morphology in chapter 2 of:

Roark, B. and Sproat, R. 2007. Computational Approaches to Morphology and
Syntax. Oxford: Oxford University Press.

Following that work, all affixation is treated via composition, since that is
the most general single regular operation that can handle morphological
processes. For example, suffixing an "s" to a word, with a morpheme boundary "+"
is modeled as the following "shape":

sigma ("" : "+s")

i.e. an insertion of "+s" after anything, where sigma represents a string
of any symbol except the boundary symbol. If one wanted to also constrain the
stem to be of a particular shape (e.g. comparative affixation in English, where
a stem must be at most two syllables long) or even to modify the stem to be a
particular shape (as in Yowlumne --- cf. Archangeli, D. 1984. Underspecification
in Yawelmani Phonology and Morphology. PhD Thesis, MIT) then one can replace
sigma with a more restrictive acceptor or transducer.

A paradigm consists of:

- A Category.
- A list of ParadigmSlots, which are combinations of a FeatureVector from the
  Category and a "shape" as above.
- A specification of what FeatureVector corresponds to the "lemma". For example
  in Latin nouns it would be "[case=nom][num=sg]". In Latin verbs it is the
  first person singular indicative active.
- An optional name.
- An optional set of rewrite rules to apply to forms in the paradigm.
- A boundary symbol.
- An optional parent paradigm from which this paradigm inherits.

Stems that are added to the system (function: set_stems_to_forms()) are composed
with all of the slot entries so that an FST is produced that maps from stems to
all of their possible forms, with boundary symbols and features. Thus, for a
Latin first declension noun:

    aqu -> aqu+a[case=nom][num=sg]
    aqu -> aqu+ae[case=gen][num=sg]
    aqu -> aqu+am[case=acc][num=sg]

etc. Call this "stem_to_forms".

The Paradigm then defines a few common operations:

1. Analyzer:

This is the output projection of the stem_to_forms, composed with an FST that
deletes boundary labels and features, and then inverted. Thus this maps from,
e.g.:

    aquam -> aqu+am[case=acc][num=sg]

2. Tagger:

Same as the Analyzer, but omitting the decomposition of the word into parts:

    aquam -> aquam[case=acc][num=sg]

3. Lemmatizer:

The lemmatizer is constructed by taking stem_to_forms, moving the feature labels
to the input side, inverting (so it maps from fully-formed word to stem +
features), then inflecting the stem as the lemma. Thus:

    aquam -> aqua[case=acc][num=sg]

4. Inflector.

This is the inverse of the lemmatizer:

    aqua[case=acc][num=sg] -> aquam
"""

from typing import Optional, NamedTuple, List, Union, Tuple, Sequence

import pynini
from pynini.lib import byte
from pynini.lib import features
from pynini.lib import pynutil


def build_stem_ids(min_id: int, max_id: int) -> pynini.Fst:
  """Builds the set of stem IDs.

  These are strings of the form __n__, for n in the range [min_id, max_id).

  Args:
    min_id: minimum stem ID (inclusive).
    max_id: maximum stem ID (exclusive).

  Returns:
    FST representing the stem IDs in [min_id, max_id) as strings.
  """
  return pynini.union(
      *["__{}__".format(i) for i in range(min_id, max_id)]).optimize()


class Error(Exception):
  """Errors specific to this module."""

  pass


def make_byte_star_except_boundary(
    boundary: pynini.FstLike = "+") -> pynini.Fst:
  """Helper function to make sigma star over bytes, minus the boundary symbol.

  Args:
    boundary: a string, the boundary symbol to use.

  Returns:
    An acceptor representing sigma star over bytes, minus the boundary symbol.
  """
  return pynini.difference(byte.BYTES, boundary).closure().optimize()


# Definitions that cover some common cases.


def suffix(affix: pynini.FstLike, stem_form: pynini.FstLike) -> pynini.Fst:
  """Helper function that suffixes `affix` to stem_form.

  Args:
    affix: an acceptor representing the affix, typically beginning with the
      boundary symbol.
    stem_form: a transducer representing the stem. If there are no further
      restrictions on the form of the base, this could simply be the output of
      make_byte_star_except_boundary().  However the affix may impose a
      restriction on what it may attach to, or even impose a change of shape.

  Returns:
    The concatenation of `stem_form` and the insertion of `affix`.
  """
  return stem_form + pynutil.insert(affix)


def prefix(affix: pynini.FstLike, stem_form: pynini.FstLike) -> pynini.Fst:
  """Helper function that preffixes `affix` to stem_form.

  Args:
    affix: an acceptor representing the affix, typically ending with the
      boundary symbol.
    stem_form: a transducer representing the stem. If there are no further
      restrictions on the form of the base, this could simply be the output of
      make_byte_star_except_boundary().  However the affix may impose a
      restriction on what it may attach to, or even impose a change of shape.

  Returns:
    The concatenation of the insertion of `affix` and `stem_form`.
  """
  return pynutil.insert(affix) + stem_form


class ParadigmSlot(NamedTuple):
  """A paradigm slot consisting of a phonological shape and a FeatureVector.

  The phonological shape is an FST representing the transformation that applies
  to a stem in the paradigm to transform it to the particular form. The
  FeatureVector represents the features associated with that form.
  """
  shape: pynini.Fst
  feature_vector: features.FeatureVector


class Paradigm:
  """Implementation of morphological paradigms.

  A paradigm consists of a Category, a sequence of ParadigmSlots, a
  specification of which slot feature counts as the lemma, an optional name, an
  optional set of rewrite rules to be applied in order, a boundary symbol and a
  parent paradigm from which to inherit.
  """

  def __init__(self,
               category: features.Category,
               slots: Sequence[Union[ParadigmSlot,
                                     Tuple[pynini.Fst,
                                           features.FeatureVector]]],
               lemma_feature_vector: features.FeatureVector,
               name: Optional[str] = None,
               rules: Optional[Sequence[pynini.Fst]] = None,
               boundary: str = "+",
               parent_paradigm: Optional["Paradigm"] = None):
    """Paradigm initializer.

    Args:
      category: a Category object.
      slots: a sequence of ParadigmSlots, or (fst, FeatureVector) pairs (the
        latter as a convenient shorthand).
      lemma_feature_vector: FeatureVector associated with the lemma. This must
        be one of the slots provided, otherwise the construction will fail.
      name: a string, the name of this paradigm.
      rules: a sequence of FSTs, rules to be applied to produce the surface
        forms. If rules is None, then the rules are inherited from the parent
        category if any.
      boundary: a string representing the boundary symbol.
      parent_paradigm: a Paradigm object from which to inherit.

    Raises:
        Error: Lemma form not found in slots.
    """
    self._category = category
    self._slots: List[ParadigmSlot] = [ParadigmSlot(s[0], s[1]) for s in slots]
    # Verify that the feature vectors are from the right category:
    for slot in self._slots:
      if slot.feature_vector.category != self._category:
        raise Error(f"Paradigm category {self._category} != "
                    f"feature vector category {slot.feature_vector.category}")
    self._name = name
    self._rules = list(rules) if rules is not None else None
    self._boundary = boundary
    # Acceptor representing the union of all the feature labels.
    self._feature_labels = pynini.project(self._category.feature_mapper,
                                          "input")
    # Sigma star for CDRewrite rules.
    self._sigma = pynini.union(byte.BYTES,
                               self._feature_labels).closure().optimize()
    # Rule to delete the boundary symbol.
    self._boundary_deleter = self._unconditioned_rewrite(
        pynutil.delete(self.boundary))
    # Rule to delete the boundary label and feature labels.
    self._deleter = pynini.compose(
        self._unconditioned_rewrite(pynutil.delete(self._feature_labels)),
        self._boundary_deleter).optimize()
    # Rule to translate all boundary labels into human-readable strings.
    self._feature_label_rewriter = self._unconditioned_rewrite(
        self._category.feature_mapper)
    # Inherit from the parent paradigm.
    self._parent_paradigm = parent_paradigm
    self._inherit()
    # The union of all the shapes of the affixes in the slots, concatenated with
    # the insertion of the feature vectors.
    self._shape = pynini.union(*(
        (s.shape + pynutil.insert(s.feature_vector.acceptor))
        for s in self._slots))
    # Derives the lemma form from the slot's shape, then delete all the features
    # and boundary symbol, so that it maps from the stem to the lemma without
    # the features and boundary symbol.
    self._lemma = None
    for s in self._slots:
      if s.feature_vector == lemma_feature_vector:
        self._lemma = s.shape + pynutil.insert(lemma_feature_vector.acceptor)
    if self._lemma is None:
      raise Error("Lemma form not found in slots")
    if self._rules is not None:
      for rule in self._rules:
        self._lemma @= rule
    self._lemma @= self._deleter
    self._lemma.optimize()
    # The stems to be added in set_stems_to_forms().
    self._stems = []
    # Stems to form transducer to be built in set_stems_to_forms().
    self._stems_to_forms = None
    # The analyzer, mapping from a fully formed word (e.g. "aquārum") to an
    # analysis (e.g. "aqu+ārum[case=gen][num=pl]")
    self._analyzer = None
    # The tagger, mapping from a fully formed word (e.g. "aquārum") to the
    # same string with morphosyntactic tags (e.g. "aquārum[case=gen][num=pl]").
    self._tagger = None
    # The lemmatizer, mapping from a fully formed word (e.g. "aquārum") to the
    # lemma with morphosyntactic tags (e.g. "aqua[case=gen][num=pl]").
    self._lemmatizer = None
    # Inversion of the lemmatizer.
    self._inflector = None

  def set_stems_to_forms(self, stems: Sequence[pynini.FstLike]) -> None:
    """Inflects stems for all slots, and applies any rules.

    Args:
      stems: a sequence of stems (strings, or acceptors) belonging to this
        paradigm.
    """
    self._stems.extend(stems)
    self._stems_to_forms = pynini.union(*self._stems)
    self._stems_to_forms.optimize()
    self._stems_to_forms @= self._shape
    if self._rules is not None:
      for rule in self._rules:
        self._stems_to_forms @= rule
    self._stems_to_forms.optimize()

  def _inherit(self) -> None:
    """Inherit from parent paradigm.

    Checks that the categories and boundaries match, then sets the rules for
    this paradigm from the parent if they are None. Slots in the list provided
    to this paradigm then override any in the parent that have matching feature
    vectors.

    Raises:
        Error: Paradigm category/boundary != parent paradigm category/boundary.
    """
    if self._parent_paradigm is None:
      return
    if self._category != self._parent_paradigm.category:
      raise Error(f"Paradigm category {self._category} != "
                  f"parent paradigm category {self._parent_paradigm.category}")
    if self._boundary != self._parent_paradigm.boundary:
      raise Error(f"Paradigm boundary {self._boundary} != "
                  f"parent paradigm boundary {self._parent_paradigm.boundary}")
    if self._rules is None:
      self._rules = self._parent_paradigm.rules
    # Adds parent slots if their feature vector isn't in the current slots'
    # feature vector.
    self._slots.extend(
        parent_slot for parent_slot in self._parent_paradigm.slots
        if parent_slot.feature_vector not in (
            slot.feature_vector for slot in self._slots))

  def _flip_lemmatizer_feature_labels(self,
                                      lemmatizer: pynini.Fst) -> pynini.Fst:
    """Helper function to flip lemmatizer's feature labels from input to output.

    Destructive operation.

    Args:
      lemmatizer: FST representing a partially constructed lemmatizer.

    Returns:
      Modified lemmatizer.
    """
    feature_labels = set()
    for s in self._feature_labels.states():
      aiter = self._feature_labels.arcs(s)
      while not aiter.done():
        arc = aiter.value()
        if arc.ilabel:
          feature_labels.add(arc.ilabel)
        aiter.next()
    lemmatizer.set_input_symbols(lemmatizer.output_symbols())
    for s in lemmatizer.states():
      maiter = lemmatizer.mutable_arcs(s)
      while not maiter.done():
        arc = maiter.value()
        if arc.olabel in feature_labels:
          # This assertion should always be true by construction.
          assert arc.ilabel == 0, (
              f"ilabel = "
              f"{lemmatizer.input_symbols().find(arc.ilabel)},"
              f" olabel = "
              f"{lemmatizer.output_symbols().find(arc.olabel)}")
          arc = pynini.Arc(arc.olabel, arc.ilabel, arc.weight, arc.nextstate)
          maiter.set_value(arc)
        maiter.next()
    return lemmatizer

  def _unconditioned_rewrite(self, tau: pynini.Fst) -> pynini.Fst:
    """Helper function for context-independent cdrewrites.

    Args:
      tau: Change FST, i.e. phi x psi.

    Returns:
      cdrewrite(tau, "", "", self._sigma)
    """
    return pynini.cdrewrite(tau, "", "", self._sigma).optimize()

  # The analyzer, tagger, lemmatizer, and inflector are all created lazily.

  @property
  def analyzer(self) -> Optional[pynini.Fst]:
    if self.stems_to_forms is None:
      return None
    if self._analyzer is not None:
      return self._analyzer
    self._make_analyzer()
    return self._analyzer

  def _make_analyzer(self) -> None:
    """Helper function for constructing analyzer."""
    self._analyzer = pynini.project(self._stems_to_forms, "output")
    self._analyzer @= self._deleter
    self._analyzer.invert().optimize()

  @property
  def tagger(self) -> Optional[pynini.Fst]:
    if self.analyzer is None:
      return None
    if self._tagger is not None:
      return self._tagger
    self._make_tagger()
    return self._tagger

  def _make_tagger(self) -> None:
    """Helper function for constructing tagger."""
    self._tagger = self._analyzer @ self._boundary_deleter
    self._tagger.optimize()

  @property
  def lemmatizer(self) -> Optional[pynini.Fst]:
    if self.stems_to_forms is None:
      return None
    if self._lemmatizer is not None:
      return self._lemmatizer
    self._make_lemmatizer()
    return self._lemmatizer

  def _make_lemmatizer(self) -> None:
    """Helper function for constructing lemmatizer."""
    # Breaking this down into steps for ease of readability.
    # Flips to map from form+features to stem.
    self._lemmatizer = self._stems_to_forms.copy()
    # Moves the feature labels to the input side, then invert. By construction
    # the feature labels are always concatenated to the end.
    self._flip_lemmatizer_feature_labels(self._lemmatizer)
    # Deletes boundary on the analysis side.
    self._lemmatizer @= self._boundary_deleter
    self._lemmatizer.invert()
    # Maps from the stem side to the lemma. The self._feature_labels is needed
    # to match the features that are now glommed onto the right-hand side.
    self._lemmatizer @= self._lemma + self._feature_labels
    self._lemmatizer.optimize()

  @property
  def inflector(self) -> Optional[pynini.Fst]:
    if self.lemmatizer is None:
      return None
    if self._inflector is not None:
      return self._inflector
    self._inflector = pynini.invert(self._lemmatizer)
    return self._inflector

  @property
  def category(self) -> features.Category:
    return self._category

  @property
  def slots(self) -> List[ParadigmSlot]:
    return self._slots

  @property
  def name(self) -> str:
    return self._name

  @property
  def boundary(self) -> str:
    return self._boundary

  @property
  def stems(self) -> List[pynini.FstLike]:
    return self._stems

  @property
  def stems_to_forms(self) -> Optional[pynini.Fst]:
    return self._stems_to_forms

  @property
  def feature_label_rewriter(self) -> pynini.Fst:
    return self._feature_label_rewriter

  @property
  def rules(self) -> Optional[List[pynini.Fst]]:
    return self._rules

