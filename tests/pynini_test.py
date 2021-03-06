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
# Copyright 2016 and onwards Google, Inc.
#
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Tests for the Pynini grammar compilation module."""

import collections
import functools
import math
import os
import pickle
import string
import tempfile
import unittest

# This module is designed to be import-safe.
from pynini import *

import pywrapfst

SEED = 212


class CDRewriteTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.sigstar = union(*string.ascii_letters)
    cls.sigstar.closure()
    cls.sigstar.optimize()
    cls.coronal = union("L", "N", "R", "T", "D")

  # Non-static helper.
  def TestRule(self, rule, istring, ostring):
    self.assertEqual((istring @ rule).string(), ostring)

  # A -> B / C __ D.
  def testAGoesToBInTheContextOfCAndD(self):
    a_to_b = cdrewrite(cross("A", "B"), "C", "D", self.sigstar)
    self.TestRule(a_to_b, "CADCAD", "CBDCBD")

  # A -> B / C __ #.
  def testAGoesToBInTheContextOfCAndHash(self):
    a_to_b = cdrewrite(cross("A", "B"), "C", "[EOS]", self.sigstar)
    self.TestRule(a_to_b, "CA", "CB")
    self.TestRule(a_to_b, "CAB", "CAB")

  # Pre-Latin rhotacism:
  # s > r / V __ V.
  def testRhotacism(self):
    vowel = union("A", "E", "I", "O", "V")
    rhotacism = cdrewrite(cross("S", "R"), vowel, vowel, self.sigstar)
    self.TestRule(rhotacism, "LASES", "LARES")

  # Classical-Latin "Pre-s deletion":
  # [+cor] -> 0 / __ [+str] (condition: LTR)
  def testPreSDeletion(self):
    pre_s_deletion = cdrewrite(
        cross(self.coronal, ""), "", "S[EOS]", self.sigstar)
    pre_s_deletion.optimize()
    self.TestRule(pre_s_deletion, "CONCORDS", "CONCORS")
    self.TestRule(pre_s_deletion, "PVLTS", "PVLS")  # cf. gen.sg. PVLTIS
    self.TestRule(pre_s_deletion, "HONORS", "HONOS")  # cf. gen.sg. HONORIS
    # cf. gen.sg. SANGVINIS
    self.TestRule(pre_s_deletion, "SANGVINS", "SANGVIS")

  # The same, but incorrectly applied RTL.
  def testPreSDeletionRTL(self):
    pre_s_deletion_wrong = cdrewrite(
        cross(self.coronal, ""), "", "S[EOS]", self.sigstar, direction="rtl")
    # Should be CONCORS.
    self.TestRule(pre_s_deletion_wrong, "CONCORDS", "CONCOS")

  # Prothesis in loanwords in Hindi (informally):
  # 0 -> i / # __ [+str] [-cor, +con]
  def testProthesis(self):
    non_coronal_consonant = union("M", "P", "B", "K", "G")
    prothesis = cdrewrite(
        cross("", "I"), "[BOS]", "S" + non_coronal_consonant, self.sigstar)
    self.TestRule(prothesis, "SKUUL", "ISKUUL")  # "school"

  # TD-deletion in English:
  # [+cor, +obst, -cont] -> 0 / [+cons] __ # (conditions: LTR, optional)
  def testTDDeletion(self):
    cons = union("M", "P", "B", "F", "V", "N", "S", "Z", "T", "D", "L", "K",
                 "G")  # etc.
    td_deletion = cdrewrite(
        cross(union("T", "D"), ""),
        cons,
        "[EOS]",
        self.sigstar,
        direction="ltr",
        mode="opt")
    # Asserts that both are possible.
    self.assertEqual(
        optimize(project("FIST" @ td_deletion, "output")),
        optimize(union("FIS", "FIST")))

  def testLambdaTransducerRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(cross("A", "B"), cross("C", "D"), "E", self.sigstar)

  def testRhoTransducerRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(cross("A", "B"), "C", cross("D", "E"), self.sigstar)

  def testWeightedLambdaRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(
          cross("A", "B"), accep("C", weight=2), "D", self.sigstar)

  def testWeightedRhoRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(
          cross("A", "B"), "C", accep("D", weight=2), self.sigstar)


class ClosureTest(unittest.TestCase):

  def testRangeClosure(self):
    m = 3
    n = 7
    cheese = "Red Windsor"
    ac = accep(cheese)
    ac.closure(m, n)
    # Doesn't accept <3 copies.
    for i in range(m):
      self.assertEqual(compose(ac, cheese * i).num_states(), 0)
    # Accepts between 3-7 copies.
    for i in range(m, n + 1):
      self.assertNotEqual(compose(ac, cheese * i).num_states(), 0)
    # Doesn't accept more than 7 copies.
    self.assertEqual(compose(ac, cheese * (n + 1)).num_states(), 0)


class DifferenceTest(unittest.TestCase):

  def testDifferenceWithUnion(self):
    ab = union("a", "b")
    abc = union(ab, "c")
    self.assertEqual(difference(abc, ab).optimize(), "c")


class DowncastTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.f = pywrapfst.VectorFst()
    # Epsilon machine.
    s = cls.f.add_state()
    cls.f.set_start(s)
    cls.f.set_final(s)

  def testDowncastTypesAreCorrect(self):
    self.assertIsInstance(self.f, pywrapfst.VectorFst)
    f_downcast = Fst.from_pywrapfst(self.f)
    self.assertIsInstance(f_downcast, Fst)

  def testDowncastedMutationTriggersDeepCopy(self):
    f_downcast = Fst.from_pywrapfst(self.f)
    f_downcast.delete_states()
    self.assertEqual(f_downcast.num_states(), 0)
    self.assertNotEqual(self.f.num_states(), 0)


class EqualTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.f = accep("Danish Blue")

  def testEqual(self):
    self.assertTrue(equal(self.f, self.f.copy()))

  def testEqualOperator(self):
    self.assertTrue(self.f == self.f.copy())

  def testNotEqualOperator(self):
    self.assertFalse(self.f != self.f.copy())


class ExceptionsTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.exchange = cross("Liptauer", "No")
    cls.f = Fst()
    cls.s = SymbolTable()
    cls.map_file = "tests/testdata/str.map"

  def testBadDestinationIndexAddArcDoesNotRaiseFstIndexError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    f.set_final(s)
    f.add_arc(s, Arc(0, 0, 0, -1))
    self.assertFalse(f.verify())

  def testBadIndexFinalRaisesFstIndexError(self):
    with self.assertRaises(FstIndexError):
      unused_weight = self.f.final(-1)

  def testBadIndexNumArcsRaisesFstIndexError(self):
    with self.assertRaises(FstIndexError):
      unused_n = self.f.num_arcs(-1)

  def testBadIndexNumInputEpsilonsRaisesFstIndexError(self):
    with self.assertRaises(FstIndexError):
      unused_n = self.f.num_input_epsilons(-1)

  def testBadIndexNumOutputEpsilonsRaisesFstIndexError(self):
    with self.assertRaises(FstIndexError):
      unused_n = self.f.num_output_epsilons(-1)

  def testBadIndexDeleteArcsRaisesFstIndexError(self):
    f = self.f.copy()
    with self.assertRaises(FstIndexError):
      f.delete_arcs(-1)

  def testBadIndicesDeleteStatesRaisesFstIndexError(self):
    f = self.f.copy()
    with self.assertRaises(FstIndexError):
      f.delete_states((-1, -2))

  def testBadSourceIndexAddArcRaisesFstIndexError(self):
    f = self.f.copy()
    with self.assertRaises(FstIndexError):
      f.add_arc(-1, Arc(0, 0, 0, 0))

  def testGarbageComposeFilterComposeRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = compose(self.f, self.f, compose_filter="nonexistent")

  def testGarbageComposeFilterDifferenceRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = difference(self.f, self.f, compose_filter="nonexistent")

  def testGarbageQueueTypeRmepsilonRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = rmepsilon(self.f, queue_type="nonexistent")

  def testGarbageQueueTypeShortestDistanceRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_sd = shortestdistance(self.f, queue_type="nonexistent")

  def testGarbageQueueTypeShortestPathRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = shortestpath(self.f, queue_type="nonexistent")

  def testGarbageSelectTypeRandgenRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = randgen(self.f, select="nonexistent")

  def testGarbageInputTokenTypeStringFileRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_file(self.map_file, input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringFileRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_file(self.map_file, output_token_type="nonexistent")

  def testNonexistentStringFileRaisesFstIOError(self):
    with self.assertRaises(FstIOError):
      unused_f = string_file("nonexistent")

  def testGarbageInputTokenTypeStringMapRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_map([], input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringMapRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_map([], output_token_type="nonexistent")

  def testGarbageInputTokenTypeStringPathIteratorRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_sp = self.f.paths(input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringPathIteratorRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_sp = self.f.paths(output_token_type="nonexistent")

  def testTransducerDifferenceRaisesFstArgError(self):
    with self.assertRaises(FstOpError):
      unused_f = difference(self.exchange, self.exchange)

  def testWrongWeightTypeAddArcRaisesFstOpError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    f.set_final(s)
    with self.assertRaises(FstOpError):
      f.add_arc(s, Arc(0, 0, Weight.one("log"), 0))

  def testWrongWeightTypeDeterminizeRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = determinize(self.f, weight=Weight.one("log"))

  def testWrongWeightTypeDisambiguateRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = disambiguate(self.f, weight=Weight.one("log"))

  def testWrongWeightTypePruneRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = prune(self.f, weight=Weight.one("log"))

  def testWrongWeightTypeRmepsilonRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = rmepsilon(self.f, weight=Weight.one("log"))

  def testWrongWeightTypeSetFinalRaisesFstOpError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    with self.assertRaises(FstOpError):
      f.set_final(s, Weight.one("log"))

  def testGarbageWeightTypeRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_w = Weight("nonexistent", 1)


class GeneratedSymbolsTest(unittest.TestCase):

  def testBosIndex(self):
    bos_index = 0xF8FE  # Defined in stringcompile.h.
    f = accep("[BOS]")
    aiter = f.arcs(f.start())
    self.assertFalse(aiter.done())
    arc = aiter.value()
    self.assertEqual(bos_index, arc.ilabel)
    self.assertEqual(bos_index, arc.ilabel)
    aiter.next()
    self.assertTrue(aiter.done())

  def testEosIndex(self):
    eos_index = 0xF8FF  # Defined in stringcompile.h.
    f = accep("[EOS]")
    aiter = f.arcs(f.start())
    arc = aiter.value()
    self.assertEqual(eos_index, arc.ilabel)
    self.assertEqual(eos_index, arc.olabel)
    aiter.next()
    self.assertTrue(aiter.done())

  def testGeneratedSymbols(self):
    cheese = "Parmesan"
    unused_f = accep(f"[{cheese}]")
    syms = generated_symbols()
    self.assertTrue(syms.member(cheese))


class IOTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.f = Fst()

  # Non-static helper.
  def TestFstAndTypeEquality(self, g):
    self.assertEqual(self.f, g)
    self.assertEqual(type(self.f), type(g))

  def testFileIO(self):
    tmp = os.path.join(tempfile.gettempdir(), "tmp.fst")
    self.f.write(tmp)
    try:
      g = Fst.read(tmp)
      self.TestFstAndTypeEquality(g)
    finally:
      os.remove(tmp)

  def testGarbageReadRaisesFstIOError(self):
    with self.assertRaises(FstIOError):
      unused_f = Fst.read("nonexistent")

  def testStringIO(self):
    sink = self.f.write_to_string()
    g = Fst.read_from_string(sink)
    self.TestFstAndTypeEquality(g)

  def testPickleIO(self):
    g = pickle.loads(pickle.dumps(self.f))
    self.TestFstAndTypeEquality(g)


class LenientlyComposeTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.sigstar = union(*string.ascii_letters + " ").closure().optimize()
    cls.cheese_geography = string_map(
        (("Red Leicester", "England"), ("Tilsit", "Russia"), ("Caerphilly",
                                                              "Wales"),
         ("Bel Paese", "Italy"), ("Red Windsor", "England"), ("Stilton",
                                                              "England"),
         ("Emmental", "Switzerland"), ("Norwegian Jarlsberg", "Norway"),
         ("Liptauer", "Germany"), ("Lancashire", "England"), ("White Stilton",
                                                              "England"),
         ("Danish Blue", "Denmark"), ("Double Gloucester", "England"),
         ("Cheshire", "England"), ("Dorset Blue Vinney", "England"),
         ("Brie", "France"), ("Roquefort", "France"), ("Port Salut", "France")))

  def testLenientCompositionOfOutOfDomainStringWithTransducerIsIdentity(self):
    cheese = "Wisconsin Cheddar"
    self.assertEqual(
        leniently_compose(cheese, self.cheese_geography, self.sigstar), cheese)

  def testLenientCompositionOfInDomainStringWithTransducerIsTransduced(self):
    cheese = "Lancashire"
    self.assertEqual(
        leniently_compose(cheese, self.cheese_geography,
                          self.sigstar).project("output").optimize(), "England")


class StringTest(unittest.TestCase):
  """Tests string compilation and stringification."""

  @classmethod
  def setUpClass(cls):
    cls.cheese = "Red Leicester"
    cls.reply = "I'm afraid we're fresh out of Red Leicester sir"
    cls.imported_cheese = "Pont l'Evêque"
    cls.accep_props = (
        ACCEPTOR | I_DETERMINISTIC | O_DETERMINISTIC | I_LABEL_SORTED
        | O_LABEL_SORTED | UNWEIGHTED | ACYCLIC | INITIAL_ACYCLIC | TOP_SORTED
        | ACCESSIBLE | COACCESSIBLE | STRING | UNWEIGHTED_CYCLES)

  def testUnbracketedBytestringUnweightedAcceptorCompilation(self):
    cheese = accep(self.cheese)
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testUnbracketedBytestringUnweightedTransducerCompilation(self):
    exchange = cross(self.cheese, self.reply)
    exchange.project("input")
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testUnbracketedBytestringWeightedAcceptorCompilation(self):
    cheese = accep(self.cheese, weight=Weight.one("tropical"))
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testUnbracketedBytestringWeightedTransducerCompilation(self):
    exchange = cross(self.cheese, self.reply)
    exchange.project("input")
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testUnbracketedBytestringCastingWeightedAcceptorCompilation(self):
    cheese = accep(self.cheese, weight=0)
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testBracketedCharsBytestringAcceptorCompilation(self):
    cheese = accep("".join("[{:d}]".format(ord(ch)) for ch in self.cheese))
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testUnicodeBytestringAcceptorCompilation(self):
    cheese = accep(self.imported_cheese)
    self.assertEqual(cheese, self.imported_cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testAsciiUtf8AcceptorCompilation(self):
    cheese = accep(self.cheese, token_type="utf8")
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(
        cheese.properties(self.accep_props, True), self.accep_props)

  def testEscapedBracketsBytestringAcceptorCompilation(self):
    ac = accep(r"[\[Camembert\] is a]\[cheese\]")
    # Should have 3 states accepting generated symbols, 8 accepting a byte,
    # and 1 final state.
    self.assertEqual(ac.num_states(), 12)

  def testGarbageWeightAcceptorRaisesFstBadWeightError(self):
    with self.assertRaises(FstBadWeightError):
      unused_ac = accep(self.cheese, weight="nonexistent")

  def testGarbageArcTypeAcceptorRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_ac = accep(self.cheese, arc_type="nonexistent")

  def testUnbalancedBracketsAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstStringCompilationError):
      unused_ac = accep(self.cheese + "]")

  def testUnbalancedBracketsTransducerRaisesFstStringCompilationError(self):
    with self.assertRaises(FstStringCompilationError):
      unused_tr = cross(self.cheese, "[" + self.reply)

  def testCrossProductTransducerCompilation(self):
    cheese = accep(self.cheese)
    reply = accep(self.reply)
    exchange = cross(cheese, reply)
    exchange.project("input")
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testAsciiByteStringify(self):
    self.assertEqual(accep(self.cheese).string(), self.cheese)

  def testAsciiUtf8Stringify(self):
    self.assertEqual(
        accep(self.cheese, token_type="utf8").string("utf8"), self.cheese)

  def testUtf8ByteStringify(self):
    self.assertEqual(
        accep(self.imported_cheese).string(), self.imported_cheese)

  def testAsciiByteStringifyAfterSymbolTableDeletion(self):
    ac = accep(self.cheese)
    ac.set_output_symbols(None)
    self.assertEqual(ac.string(), self.cheese)

  def testUtf8Utf8Stringify(self):
    self.assertEqual(
        accep(self.imported_cheese, token_type="utf8").string("utf8"),
        self.imported_cheese)

  def testUnicodeByteStringify(self):
    self.assertEqual(
        accep(self.imported_cheese).string(), self.imported_cheese)

  def testUnicodeUtf8Stringify(self):
    self.assertEqual(
        accep(self.imported_cheese, token_type="utf8").string("utf8"),
        self.imported_cheese)

  def testUtf8StringifyAfterSymbolTableDeletion(self):
    ac = accep(self.imported_cheese, token_type="utf8")
    ac.set_output_symbols(None)
    self.assertEqual(ac.string("utf8"), self.imported_cheese)

  def testStringifyOnNonkStringFstRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_ac = union(self.cheese, self.imported_cheese).string()

  def testCompositionOfStringAndLogArcWorks(self):
    cheese = "Greek Feta"
    self.assertEqual(cheese @ accep(cheese, arc_type="log"), cheese)

  def testCompositionOfLogArcAndStringWorks(self):
    cheese = "Tilsit"
    self.assertEqual(accep(cheese, arc_type="log") @ cheese, cheese)

  def testCompositionOfStringAndLog64ArcWorks(self):
    cheese = "Greek Feta"
    self.assertEqual(cheese @ accep(cheese, arc_type="log64"), cheese)

  def testCompositionOfLog64ArcAndStringWorks(self):
    cheese = "Tilsit"
    self.assertEqual(accep(cheese, arc_type="log64") @ cheese, cheese)

  def testLogWeightToStandardAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstOpError):
      unused_ac = accep("Sage Derby", weight=Weight.one("log"))

  def testLog64WeightToLogAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstOpError):
      unused_ac = accep(
          "Wensleydale", arc_type="log", weight=Weight.one("log64"))


class StringFileTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    # Set the directory to org_opengrm_pynini/tests/testdata" for Bazel testing.
    cls.map_file = "tests/testdata/str.map"

  def ContainsMapping(self, istring, mapper, ostring):
    lattice = compose(istring, mapper, compose_filter="alt_sequence")
    lattice.project("output").rmepsilon().arcsort("olabel")
    lattice = compose(mapper, ostring, compose_filter="sequence")
    self.assertNotEqual(lattice.start(), NO_STATE_ID)

  def testByteToByteStringFile(self):
    mapper = string_file(self.map_file)
    self.ContainsMapping("[Bel Paese]", mapper, "Sorry")
    self.ContainsMapping("Cheddar", mapper, "Cheddar")
    self.ContainsMapping("Caithness", mapper, "Pont-l'Évêque")
    self.ContainsMapping("Pont-l'Évêque", mapper, "Camembert")

  def testByteToUtf8StringFile(self):
    utf8 = functools.partial(accep, token_type="utf8")
    mapper = string_file(self.map_file, output_token_type="utf8")
    self.ContainsMapping("[Bel Paese]", mapper, utf8("Sorry"))
    self.ContainsMapping("Cheddar", mapper, utf8("Cheddar"))
    self.ContainsMapping("Caithness", mapper, utf8("Pont-l'Évêque"))
    self.ContainsMapping("Pont-l'Évêque", mapper, utf8("Camembert"))

  def testUtf8ToUtf8StringFile(self):
    utf8 = functools.partial(accep, token_type="utf8")
    mapper = string_file(
        self.map_file, input_token_type="utf8", output_token_type="utf8")
    self.ContainsMapping(utf8("[Bel Paese]"), mapper, utf8("Sorry"))
    self.ContainsMapping(utf8("Pont-l'Évêque"), mapper, utf8("Camembert"))

  def testByteToSymbolStringFile(self):
    syms = SymbolTable()
    syms.add_symbol("<epsilon>")
    syms.add_symbol("Sorry")
    syms.add_symbol("Cheddar")
    syms.add_symbol("Pont-l'Évêque")
    syms.add_symbol("Camembert")
    mapper = string_file(self.map_file, output_token_type=syms)
    symc = functools.partial(accep, token_type=syms)
    self.ContainsMapping("[Bel Paese]", mapper, symc("Sorry"))
    self.ContainsMapping("Pont-l'Évêque", mapper, symc("Camembert"))


class StringMapTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    # In-Python version of str.map.
    cls.lines = [("[Bel Paese]", "Sorry"), "Cheddar",
                 ("Caithness", "Pont-l'Évêque", ".666"),
                 ("Pont-l'Évêque", "Camembert")]

  def ContainsMapping(self, istring, mapper, ostring):
    lattice = compose(istring, mapper, compose_filter="alt_sequence")
    lattice.project("output").rmepsilon().arcsort("olabel")
    lattice = compose(mapper, ostring, compose_filter="sequence")
    self.assertNotEqual(lattice.start(), NO_STATE_ID)

  def testByteToByteStringMap(self):
    mapper = string_map(self.lines)
    self.ContainsMapping("[Bel Paese]", mapper, "Sorry")
    self.ContainsMapping("Cheddar", mapper, "Cheddar")
    self.ContainsMapping("Caithness", mapper, "Pont-l'Évêque")
    self.ContainsMapping("Pont-l'Évêque", mapper, "Camembert")

  def testByteToUtf8StringMap(self):
    mapper = string_map(self.lines, output_token_type="utf8")
    utf8 = functools.partial(accep, token_type="utf8")
    self.ContainsMapping("[Bel Paese]", mapper, utf8("Sorry"))
    self.ContainsMapping("Cheddar", mapper, utf8("Cheddar"))
    self.ContainsMapping("Caithness", mapper, utf8("Pont-l'Évêque"))
    self.ContainsMapping("Pont-l'Évêque", mapper, utf8("Camembert"))

  def testUtf8ToUtf8StringMap(self):
    mapper = string_map(
        self.lines, input_token_type="utf8", output_token_type="utf8")
    utf8 = functools.partial(accep, token_type="utf8")
    self.ContainsMapping(utf8("[Bel Paese]"), mapper, utf8("Sorry"))
    self.ContainsMapping(utf8("Pont-l'Évêque"), mapper, utf8("Camembert"))

  def testByteToSymbolStringMap(self):
    syms = SymbolTable()
    syms.add_symbol("<epsilon>")
    syms.add_symbol("Sorry")
    syms.add_symbol("Cheddar")
    syms.add_symbol("Pont-l'Évêque")
    syms.add_symbol("Camembert")
    mapper = string_map(self.lines, output_token_type=syms)
    symc = functools.partial(accep, token_type=syms)
    self.ContainsMapping("[Bel Paese]", mapper, symc("Sorry"))
    self.ContainsMapping("Pont-l'Évêque", mapper, symc("Camembert"))


class StringPathIteratorTest(unittest.TestCase):

  # Implements this, in the case of Python 2.7.

  def assertCountEqual(self, arg1, arg2):
    self.assertEqual(collections.Counter(arg1), collections.Counter(arg2))

  @classmethod
  def setUpClass(cls):
    cls.triples = [("Bel Paese", "Sorry", "4"),
                   ("Red Windsor",
                    "Normally, sir, yes, but today the van broke down.", "3"),
                   ("Stilton", "Sorry", "2")]
    cls.f = string_map(cls.triples)

  def testStringPathIteratorIStrings(self):
    self.assertCountEqual(self.f.paths().istrings(),
                          (t[0] for t in self.triples))

  def testStringPathsIStrings(self):
    self.assertCountEqual(self.f.paths().istrings(),
                          (t[0] for t in self.triples))

  def testStringPathsOStrings(self):
    self.assertCountEqual(self.f.paths().ostrings(),
                          (t[1] for t in self.triples))

  def testStringPathsWeights(self):
    self.assertCountEqual((str(w) for w in self.f.paths().weights()),
                          (str(t[2]) for t in self.triples))

  def testStringPathsAfterFstDeletion(self):
    cheeses = ("Pipo Crem'", "Fynbo")
    f = union(*cheeses)
    sp = f.paths()
    del f  # Should be garbage-collected immediately.
    self.assertCountEqual(sp.ostrings(), cheeses)

  def testStringPathLabelsWithEpsilons(self):
    # Note that the Thompson construction for union connects the initial state
    # of the first FST to the initial state of the second FST with an
    # epsilon-arc, a fact we take advantage of here.
    cheeses = ("Ilchester", "Limburger")
    f = union(*cheeses)
    self.assertCountEqual(cheeses, f.paths().ostrings())


class SymbolTableTest(unittest.TestCase):

  def testPickleIO(self):
    f = SymbolTable()
    f.add_symbol("<epsilon>")
    f.add_symbol("Dorset Blue Vinney")
    g = pickle.loads(pickle.dumps(f))
    self.assertEqual(f.labeled_checksum(), g.labeled_checksum())


class TransducerTest(unittest.TestCase):

  def testPrecompiledLogCrossProduct(self):
    upper = accep("Smoked Austrian", arc_type="log")
    lower = accep("No", arc_type="log")
    tr = cross(upper, lower)
    self.assertEqual(tr.arc_type(), "log")

  def testImplicitLeftLogCrossProducts(self):
    tr = cross("Smoked Austrian", accep("No", arc_type="log"))
    self.assertEqual(tr.arc_type(), "log")

  def testImplicitRightLogCrossProducts(self):
    tr = cross(accep("Smoked Austrian", arc_type="log"), "No")
    self.assertEqual(tr.arc_type(), "log")


class WeightTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    half = -math.log(.5)
    one_half = -math.log(1.5)
    two = -math.log(2)
    cls.delta = 1. / 1024.
    cls.tropical_zero = Weight.zero("tropical")
    cls.tropical_half = Weight("tropical", half)
    cls.tropical_one = Weight.one("tropical")
    cls.log_zero = Weight.zero("log")
    cls.log_half = Weight("log", half)
    cls.log_one = Weight.one("log")
    cls.log_one_half = Weight("log", one_half)
    cls.log_two = Weight("log", two)
    cls.log64_zero = Weight.zero("log64")
    cls.log64_half = Weight("log64", half)
    cls.log64_one = Weight.one("log64")
    cls.log64_one_half = Weight("log64", one_half)
    cls.log64_two = Weight("log64", two)

  # Helper.

  def assertApproxEquals(self, w1, w2):
    self.assertAlmostEqual(float(w1), float(w2), self.delta)

  # Tropical weights.

  def testTropicalZeroPlusZeroEqualsZero(self):
    zero = self.tropical_zero
    self.assertEqual(plus(zero, zero), zero)

  def testTropicalOnePlusOneEqualsOne(self):
    one = self.tropical_one
    self.assertEqual(plus(one, one), one)

  def testTropicalOnePlusZeroEqualsOne(self):
    one = self.tropical_one
    zero = self.tropical_zero
    self.assertEqual(plus(one, zero), one)
    self.assertEqual(plus(zero, one), one)

  def testTropicalHalfPlusHalfEqualsHalf(self):
    half = self.tropical_half
    self.assertEqual(plus(half, half), half)

  def testTropicalZeroTimesZeroEqualsZero(self):
    zero = self.tropical_zero
    self.assertEqual(times(zero, zero), zero)

  def testTropicalOneTimesOneEqualsOne(self):
    one = self.tropical_one
    self.assertEqual(times(one, one), one)

  def testTropicalOneTimesZeroEqualsZero(self):
    one = self.tropical_one
    zero = self.tropical_zero
    self.assertEqual(times(one, zero), zero)
    self.assertEqual(times(zero, one), zero)

  def testTropicalHalfTimesOneEqualsHalf(self):
    half = self.tropical_half
    one = self.tropical_one
    self.assertEqual(times(half, one), half)
    self.assertEqual(times(one, half), half)

  def testTropicalZeroDivideOneEqualsZero(self):
    zero = self.tropical_zero
    one = self.tropical_one
    self.assertEqual(divide(zero, one), zero)

  def testTropicalOneDivideZeroRaisesFstBadWeightError(self):
    zero = self.tropical_zero
    one = self.tropical_one
    with self.assertRaises(FstBadWeightError):
      unused_w = divide(one, zero)

  def testTropicalZeroDivideZeroRaisesFstBadWeightError(self):
    zero = self.tropical_zero
    with self.assertRaises(FstBadWeightError):
      unused_w = divide(zero, zero)

  def testTropicalOneDivideOneEqualsOne(self):
    one = self.tropical_one
    self.assertEqual(divide(one, one), one)

  def testTropicalOneToTheTenthPowerEqualsOne(self):
    one = self.tropical_one
    self.assertEqual(power(one, 10), one)

  def testTropicalZeroToTheZerothPowerEqualsOne(self):
    zero = self.tropical_zero
    one = self.tropical_one
    self.assertEqual(power(zero, 0), one)

  # Log weights.

  def testLogZeroPlusZeroEqualsZero(self):
    zero = self.log_zero
    self.assertEqual(plus(zero, zero), zero)

  def testLogOnePlusOneEqualsTwo(self):
    one = self.log_one
    two = self.log_two
    self.assertApproxEquals(plus(one, one), two)

  def testLogOnePlusZeroEqualsOne(self):
    one = self.log_one
    zero = self.log_zero
    self.assertEqual(plus(one, zero), one)
    self.assertEqual(plus(zero, one), one)

  def testLogHalfPlusHalfEqualsOneHalf(self):
    half = self.log_half
    one = self.log_one
    one_half = self.log_one_half
    self.assertApproxEquals(plus(half, one), one_half)

  def testLogZeroTimesZeroEqualsZero(self):
    zero = self.log_zero
    self.assertEqual(times(zero, zero), zero)

  def testLogOneTimesOneEqualsOne(self):
    one = self.log_one
    self.assertEqual(times(one, one), one)

  def testLogOneTimesZeroEqualsZero(self):
    one = self.log_one
    zero = self.log_zero
    self.assertEqual(times(one, zero), zero)
    self.assertEqual(times(zero, one), zero)

  def testLogHalfTimesOneEqualsHalf(self):
    half = self.log_half
    one = self.log_one
    self.assertEqual(times(half, one), half)
    self.assertEqual(times(one, half), half)

  def testLogZeroDivideOneEqualsZero(self):
    zero = self.log_zero
    one = self.log_one
    self.assertEqual(divide(zero, one), zero)

  def testLogOneDivideZeroRaisesBadWeightError(self):
    zero = self.log_zero
    one = self.log_one
    with self.assertRaises(FstBadWeightError):
      unused_w = self.assertEqual(divide(one, zero), zero)

  def testLogZeroDivideZeroRaisesFstBadWeightError(self):
    zero = self.log_zero
    with self.assertRaises(FstBadWeightError):
      unused_w = self.assertEqual(divide(zero, zero), zero)

  def testLogOneDivideOneEqualsOne(self):
    one = self.log_one
    self.assertEqual(divide(one, one), one)

  def testLogOneToTheTenthPowerEqualsOne(self):
    one = self.log_one
    self.assertEqual(power(one, 10), one)

  def testLogZeroToTheZerothPowerEqualsOne(self):
    zero = self.log_zero
    one = self.log_one
    self.assertEqual(power(zero, 0), one)

  # Log64 weights.

  def testLog64ZeroPlusZeroEqualsZero(self):
    zero = self.log64_zero
    self.assertEqual(plus(zero, zero), zero)

  def testLog64OnePlusOneEqualsTwo(self):
    one = self.log64_one
    two = self.log64_two
    self.assertApproxEquals(plus(one, one), two)

  def testLog64OnePlusZeroEqualsOne(self):
    one = self.log64_one
    zero = self.log64_zero
    self.assertEqual(plus(one, zero), one)
    self.assertEqual(plus(zero, one), one)

  def testLog64HalfPlusHalfEqualsOneHalf(self):
    half = self.log64_half
    one = self.log64_one
    one_half = self.log64_one_half
    self.assertApproxEquals(plus(half, one), one_half)

  def testLog64ZeroTimesZeroEqualsZero(self):
    zero = self.log64_zero
    self.assertEqual(times(zero, zero), zero)

  def testLog64OneTimesOneEqualsOne(self):
    one = self.log64_one
    self.assertEqual(times(one, one), one)

  def testLog64OneTimesZeroEqualsZero(self):
    one = self.log64_one
    zero = self.log64_zero
    self.assertEqual(times(one, zero), zero)
    self.assertEqual(times(zero, one), zero)

  def testLog64HalfTimesOneEqualsHalf(self):
    half = self.log64_half
    one = self.log64_one
    self.assertEqual(times(half, one), half)
    self.assertEqual(times(one, half), half)

  def testLog64ZeroDivideOneEqualsZero(self):
    zero = self.log64_zero
    one = self.log64_one
    self.assertEqual(divide(zero, one), zero)

  def testLog64OneDivideZeroRaisesBadWeightError(self):
    zero = self.log64_zero
    one = self.log64_one
    with self.assertRaises(FstBadWeightError):
      unused_w = self.assertEqual(divide(one, zero), zero)

  def testLog64ZeroDivideZeroRaisesFstBadWeightError(self):
    zero = self.log64_zero
    with self.assertRaises(FstBadWeightError):
      unused_w = self.assertEqual(divide(zero, zero), zero)

  def testLog64OneDivideOneEqualsOne(self):
    one = self.log64_one
    self.assertEqual(divide(one, one), one)

  def testLog64ToTheTenthPowerEqualsOne(self):
    one = self.log64_one
    self.assertEqual(power(one, 10), one)

  def testLog64ToTheZerothPowerEqualsOne(self):
    zero = self.log64_zero
    one = self.log64_one
    self.assertEqual(power(zero, 0), one)


class WorkedExampleTest(unittest.TestCase):

  def testWorkedExample(self):
    pairs = zip(string.ascii_lowercase, string.ascii_uppercase)
    self.upcaser = string_map(pairs).closure()
    self.downcaser = invert(self.upcaser)
    awords = "You do have some cheese do you".lower().split()
    for aword in awords:
      result = (aword @ self.upcaser).project("output").optimize()
      self.assertEqual(result, aword.upper())
    cheese = "Parmesan".lower()
    cascade = (
        cheese @ self.upcaser @ self.downcaser @ self.upcaser @ self.downcaser)
    self.assertEqual(cascade.string(), cheese)


if __name__ == "__main__":
  unittest.main()
