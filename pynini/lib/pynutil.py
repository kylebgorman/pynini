# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Simple utility functions.

Please do not overly-specific functions or introduce additional dependencies
(i.e., beyond Pynini itself) to this module.
"""

from typing import Optional

import pynini


def insert(expr: pynini.FstLike,
           weight: Optional[pynini.WeightLike] = None) -> pynini.Fst:
  result = pynini.cross("", expr)
  if weight is not None:
    result.concat(pynini.acceptor("", weight=weight))
  return result


def delete(expr: pynini.FstLike,
           weight: Optional[pynini.WeightLike] = None) -> pynini.Fst:
  result = pynini.cross(expr, "")
  if weight is not None:
    result.concat(pynini.acceptor("", weight=weight))
  return result

