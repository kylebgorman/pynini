# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Edit transducer classes.

Edit transducers are abstract machines used to efficiently compute edit
distance and approximate string matches.

Here, we provide three concrete classes:

* EditTransducer(object): Constructs the transducer from an input alphabet and
  cost matrix. Provides a protected `_create_lattice` method for lattice
  construction, which may be overridden by derived classes.
* LevenshteinDistance(EditTransducer): Also adds a method for computing
  Levenshtein distance from the lattice.
* LevenshteinAutomaton(LevenshteinDistance): Uses the edit transducer and an
  input vocabulary to construct a right-factored lexicon from which one can
  compute the closest matches.
"""

from typing import Iterable, List

import pynini
from pynini.lib import pynutil

DEFAULT_INSERT_COST = 1.
DEFAULT_DELETE_COST = 1.
DEFAULT_SUBSTITUTE_COST = 1.


class Error(Exception):
  """Errors specific to this module."""

  pass


class EditTransducer(object):
  """Factored edit transducer.

  This class stores the two factors of an finite-alphabet edit transducer and
  supports insertion, deletion, and substitution operations with user-specified
  costs.

  Note that the cost of substitution must be less than the cost of insertion
  plus the cost of deletion or no optimal path will include substitution.
  """

  # Reserved labels for edit operations.
  DELETE = "<delete>"
  INSERT = "<insert>"
  SUBSTITUTE = "<substitute>"

  def __init__(self,
               alphabet: Iterable[str],
               insert_cost: float = DEFAULT_INSERT_COST,
               delete_cost: float = DEFAULT_DELETE_COST,
               substitute_cost: float = DEFAULT_SUBSTITUTE_COST):
    """Constructor.

    Args:
      alphabet: edit alphabet (an iterable of strings).
      insert_cost: the cost for the insertion operation.
      delete_cost: the cost for the deletion operation.
      substitute_cost: the cost for the substitution operation.
    """
    # Left factor; note that we divide the edit costs by two because they also
    # will be incurred when traversing the right factor.
    match = pynini.union(*alphabet).optimize()
    i_insert = pynutil.insert(f"[{self.INSERT}]", weight=insert_cost / 2)
    i_delete = pynini.cross(
        match, pynini.acceptor(f"[{self.DELETE}]", weight=delete_cost / 2))
    i_substitute = pynini.cross(
        match,
        pynini.acceptor(f"[{self.SUBSTITUTE}]", weight=substitute_cost / 2))
    i_ops = pynini.union(match, i_insert, i_delete, i_substitute).optimize()
    # Right factor; this is constructed by inverting the left factor (i.e.,
    # swapping the input and output labels), then swapping the insert and delete
    # labels on what is now the input side.
    o_ops = pynini.invert(i_ops)
    syms = pynini.generated_symbols()
    insert_label = syms.find(self.INSERT)
    delete_label = syms.find(self.DELETE)
    pairs = [(insert_label, delete_label), (delete_label, insert_label)]
    o_ops.relabel_pairs(ipairs=pairs)
    # Computes the closure for both sets of ops.
    self._e_i = i_ops.closure().optimize()
    self._e_o = o_ops.closure().optimize()

  @staticmethod
  def check_wellformed_lattice(lattice: pynini.Fst) -> None:
    """Raises an error if the lattice is empty.

    Args:
      lattice: A lattice FST.

    Raises:
      Error: Lattice is empty.
    """
    if lattice.start() == pynini.NO_STATE_ID:
      raise Error("Lattice is empty")

  def _create_lattice(self, iexpr: pynini.FstLike,
                      oexpr: pynini.FstLike) -> pynini.Fst:
    """Creates edit lattice for a pair of input/output strings or acceptors.

    Args:
      iexpr: input string or acceptor
      oexpr: output string or acceptor.

    Returns:
      A lattice FST.
    """
    lattice = (iexpr @ self._e_i) @ (self._e_o @ oexpr)
    EditTransducer.check_wellformed_lattice(lattice)
    return lattice


class LevenshteinDistance(EditTransducer):
  """Edit transducer augmented with a distance calculator."""

  def distance(self, iexpr: pynini.FstLike, oexpr: pynini.FstLike) -> float:
    """Computes minimum distance.

    This method computes, for a pair of input/output strings or acceptors, the
    minimum edit distance according to the underlying edit transducer.

    Args:
      iexpr: input string or acceptor.
      oexpr: output string or acceptor.

    Returns:
      Minimum edit distance according to the edit transducer.
    """
    lattice = self._create_lattice(iexpr, oexpr)
    # The shortest cost from all final states to the start state is
    # equivalent to the cost of the shortest path.
    return float(
        pynini.shortestdistance(lattice, reverse=True)[lattice.start()])


class LevenshteinAutomaton(LevenshteinDistance):
  """Edit transducer with a fixed output lexicon and closest-match methods."""

  def __init__(self,
               alphabet: Iterable[str],
               lexicon: Iterable[str],
               insert_cost: float = DEFAULT_INSERT_COST,
               delete_cost: float = DEFAULT_DELETE_COST,
               substitute_cost: float = DEFAULT_SUBSTITUTE_COST):
    super(LevenshteinAutomaton, self).__init__(alphabet, insert_cost,
                                               delete_cost, substitute_cost)
    # Compiles lexicon and composes the right factor with it.
    compiled_lexicon = pynini.union(*lexicon)
    self._l_o = self._e_o @ compiled_lexicon
    self._l_o.optimize(True)

  def _create_levenshtein_automaton_lattice(
      self, query: pynini.FstLike) -> pynini.Fst:
    """Constructs a lattice for a query string.

    Args:
      query: input string or acceptor.

    Returns:
      A lattice FST.
    """
    lattice = query @ self._e_i @ self._l_o
    EditTransducer.check_wellformed_lattice(lattice)
    return lattice

  def closest_match(self, query: pynini.FstLike) -> str:
    """Returns the closest string to the query in the lexicon.

    This method computes, for an input string or acceptor, the closest string
    in the lexicon according to the underlying edit transducer. In the case of
    a tie (i.e., where there are multiple closest strings), only one will be
    returned; tie breaking is deterministic but difficult to reason about and
    thus should be considered unspecified.) The `closest_matches` method can be
    used to enumerate all the ties.

    Args:
      query: input string or acceptor.

    Returns:
      The closest string in the lexicon.
    """
    lattice = self._create_levenshtein_automaton_lattice(query)
    return pynini.shortestpath(lattice).string()

  def closest_matches(self, query: pynini.FstLike) -> List[str]:
    """Returns all of the closest strings to the query in the lexicon.

    This method returns, for an input string or acceptor, the closest strings
    in the lexicon according to the underlying edit transducer. A string is
    "closest" if it has the same edit distance as the closest string. The order
    in which the strings are returned is deterministic but difficult to reason
    about and thus should be considered unspecified.

    Args:
      query: input string or acceptor.

    Returns:
      A list of the closest strings in the lexicon.
    """
    lattice = self._create_levenshtein_automaton_lattice(query)
    lattice.project("output").rmepsilon()
    # Prunes all paths whose weights are worse than the best path.
    return list(pynini.determinize(lattice, weight=0).paths().ostrings())

