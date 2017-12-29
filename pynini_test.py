# Encoding: UTF-8
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.


"""Tests for the Pynini grammar compilation module."""


import math
import string
import unittest


# This module is designed to be import-safe.
from pynini import *


SEED = 212


class PyniniCDRewriteTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.sigstar = union(*string.letters)
    cls.sigstar.closure()
    cls.sigstar.optimize()
    cls.coronal = union("L", "N", "R", "T", "D")

  # Non-static helper.
  def TestRule(self, rule, istring, ostring):
    self.assertEqual((istring * rule).stringify(), ostring)

  # A -> B / C __ D.
  def testAGoesToBInTheContextOfCAndD(self):
    a_to_b = cdrewrite(transducer("A", "B"), "C", "D", self.sigstar)
    self.TestRule(a_to_b, "CADCAD", "CBDCBD")

  # Pre-Latin rhotacism:
  # s > r / V __ V.
  def testRhotacism(self):
    vowel = union("A", "E", "I", "O", "V")
    rhotacism = cdrewrite(transducer("S", "R"), vowel, vowel, self.sigstar)
    self.TestRule(rhotacism, "LASES", "LARES")

  # Classical-Latin "Pre-s deletion":
  # [+cor] -> 0 / __ [+str] (condition: LTR)
  def testPreSDeletion(self):
    pre_s_deletion = cdrewrite(transducer(self.coronal, ""), "", "S[EOS]",
                               self.sigstar)
    pre_s_deletion.optimize()
    self.TestRule(pre_s_deletion, "CONCORDS", "CONCORS")
    self.TestRule(pre_s_deletion, "PVLTS", "PVLS")        # cf. gen.sg. PVLTIS
    self.TestRule(pre_s_deletion, "HONORS", "HONOS")      # cf. gen.sg. HONORIS
    # cf. gen.sg. SANGVINIS
    self.TestRule(pre_s_deletion, "SANGVINS", "SANGVIS")

  # The same, but incorrectly applied RTL.
  def testPreSDeletionRTL(self):
    pre_s_deletion_wrong = cdrewrite(transducer(self.coronal, ""), "",
                                     "S[EOS]", self.sigstar, direction="rtl")
    # Should be CONCORS.
    self.TestRule(pre_s_deletion_wrong, "CONCORDS", "CONCOS")

  # Prothesis in loanwords in Hindi (informally):
  # 0 -> i / # __ [+str] [-cor, +con]
  def testProthesis(self):
    non_coronal_consonant = union("M", "P", "B", "K", "G")
    prothesis = cdrewrite(transducer("", "I"), "[BOS]",
                          "S" + non_coronal_consonant, self.sigstar)
    self.TestRule(prothesis, "SKUUL", "ISKUUL")  # "school"

  # TD-deletion in English:
  # [+cor, +obst, -cont] -> 0 / [+cons] __ # (conditions: LTR, optional)
  def testTDDeletion(self):
    cons = union("M", "P", "B", "F", "V", "N", "S", "Z", "T", "D", "L", "K",
                 "G")  # etc.
    td_deletion = cdrewrite(transducer(union("T", "D"), ""), cons, "[EOS]",
                            self.sigstar, direction="ltr", mode="opt")
    # Asserts that both are possible.
    self.assertEqual(optimize(project("FIST" * td_deletion, True)),
                     optimize(union("FIS", "FIST")))

  def testLambdaTransducerRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(transducer("[phi]", "[psi]"),
                           transducer("[lambda]", "[lambda_prime]"),
                           "[rho]", self.sigstar)

  def testRhoTransducerRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(transducer("[phi]", "[psi]"), "[lambda]",
                           transducer("[rho]", "[rho_prime]"), self.sigstar)

  def testWeightedLambdaRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = (
          cdrewrite(
              transducer("[phi]", "[psi]"), acceptor("[lambda]", 2),
              "[rho]", self.sigstar))

  def testWeightedRhoRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = cdrewrite(transducer("[phi]", "[psi]"), "[lambda]",
                           acceptor("[rho]", 2), self.sigstar)


class PyniniClosureTest(unittest.TestCase):

  def testRangeClosure(self):
    m = 3
    n = 7
    cheese = "Red Windsor"
    ac = acceptor(cheese)
    ac.closure(m, n)
    # Doesn't accept <3 copies.
    for i in xrange(m):
      self.assertEqual(compose(ac, cheese * i).num_states(), 0)
    # Accepts between 3-7 copies.
    for i in xrange(m, n + 1):
      self.assertNotEqual(compose(ac, cheese * i).num_states(), 0)
    # Doesn't accept more than 7 copies.
    self.assertEqual(compose(ac, cheese * (n + 1)).num_states(), 0)


class PyniniContainmentTest(unittest.TestCase):

  def testContainment(self):
    ifst = a("Limburger")
    sigma_star = u(*string.ascii_letters + ".?! ").closure().optimize()
    cont = containment(ifst, sigma_star)
    istring = ("Have you got...SHUT THAT BLOODY BOUZOUKI UP?!..."
               "have you got any Limburger?")
    ostring = (istring * cont).stringify()
    self.assertEqual(istring, ostring)


class PyniniDifferenceTest(unittest.TestCase):

  def testDifferenceWithUnion(self):
    ab = u("a", "b")
    abc = u(ab, "c")
    self.assertEqual(difference(abc, ab).optimize(), "c")


class PyniniEpsilonMachineTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.final_weight = 1.5
    cls.f = epsilon_machine("log64", cls.final_weight)

  def testLog64EpsilonMachineHasRightTopology(self):
    self.assertEqual(self.f.num_states(), 1)
    self.assertEqual(self.f.start(), 0)
    self.assertEqual(self.f.num_arcs(self.f.start()), 0)

  def testEpsilonMachineHasFinalWeight(self):
    self.assertEqual(self.f.final(self.f.start()),
                     Weight(self.f.weight_type(), self.final_weight))


class PyniniEqualTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.f = acceptor("Danish Blue")

  def testEqual(self):
    self.assertTrue(equal(self.f, self.f.copy()))

  def testEqualOperator(self):
    self.assertTrue(self.f == self.f.copy())

  def testNotEqualOperator(self):
    self.assertFalse(self.f != self.f.copy())



class PyniniExceptionsTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.exchange = transducer("Liptauer", "No")
    cls.f = Fst()
    cls.s = SymbolTable()
    cls.map_file = "testdata/cheese.map"

  def testBadDestinationIndexAddArcDoesNotRaiseFstIndexError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    f.set_final(s)
    f.add_arc(s, Arc(0, 0, 0, -1))
    self.assertFalse(f.verify())

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

  def testGarbageCallArcLabelingReplaceRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = replace(
          self.f, (("f", self.f),), call_arc_labeling="nonexistent")


  def testGarbageReturnArcLabelingReplaceRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = replace(
          self.f, (("f", self.f),), call_arc_labeling="nonexistent")

  def testGarbageInputTokenTypeStringFileRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_file(self.map_file, input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringFileRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_file(self.map_file, output_token_type="nonexistent")

  def testGarbageInputTokenTypeStringMapRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_map([], input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringMapRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_f = string_map([], output_token_type="nonexistent")

  def testGarbageInputTokenTypeStringPathsRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_sp = StringPaths(self.f, input_token_type="nonexistent")

  def testGarbageOutputTokenTypeStringPathsRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_sp = StringPaths(self.f, output_token_type="nonexistent")

  def testTransducerDifferenceRaisesFstArgError(self):
    with self.assertRaises(FstOpError):
      unused_f = difference(self.exchange, self.exchange)

  def testWrongWeightTypeAddArcRaisesFstOpError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    f.set_final(s)
    with self.assertRaises(FstOpError):
      f.add_arc(s, Arc(0, 0, Weight.One("log"), 0))

  def testWrongWeightTypeDeterminizeRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = determinize(self.f, weight=Weight.One("log"))

  def testWrongWeightTypeDisambiguateRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = disambiguate(self.f, weight=Weight.One("log"))

  def testWrongWeightTypePruneRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = prune(self.f, weight=Weight.One("log"))

  def testWrongWeightTypeRmepsilonRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_f = rmepsilon(self.f, weight=Weight.One("log"))

  def testWrongWeightTypeSetFinalRaisesFstOpError(self):
    f = self.f.copy()
    s = f.add_state()
    f.set_start(s)
    with self.assertRaises(FstOpError):
      f.set_final(s, Weight.One("log"))

  def testGarbageWeightTypeRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_w = Weight("nonexistent", 1)


class PyniniLenientlyComposeTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.sigstar = u(*string.ascii_letters + " ").closure().optimize()
    cls.cheese_geography = string_map((("Red Leicester", "England"),
                                       ("Tilsit", "Russia"),
                                       ("Caerphilly", "Wales"),
                                       ("Bel Paese", "Italy"),
                                       ("Red Windsor", "England"),
                                       ("Stilton", "England"),
                                       ("Emmental", "Switzerland"),
                                       ("Norwegian Jarlsberg", "Norway"),
                                       ("Liptauer", "Germany"),
                                       ("Lancashire", "England"),
                                       ("White Stilton", "England"),
                                       ("Danish Blue", "Denmark"),
                                       ("Double Gloucester", "England"),
                                       ("Cheshire", "England"),
                                       ("Dorset Blue Vinney", "England"),
                                       ("Brie", "France"),
                                       ("Roquefort", "France"),
                                       ("Port Salut", "France")))

  def testLenientCompositionOfOutOfDomainStringWithTransducerIsIdentity(self):
    cheese = "Wisconsin Cheddar"
    self.assertEqual(leniently_compose(cheese, self.cheese_geography,
                                       self.sigstar), cheese)

  def testLenientCompositionOfInDomainStringWithTransducerIsTransduced(self):
    cheese = "Lancashire"
    self.assertEqual(leniently_compose(cheese, self.cheese_geography,
                                       self.sigstar).project(True).optimize(),
                     "England")


class PyniniMatchesTest(unittest.TestCase):

  def testMatches(self):
    m1 = "abc123"
    m2 = u("a", "b", "c", "1", "2", "3").closure()
    self.assertTrue(matches(m1, m2))

  def testNotMatch(self):
    m1 = "abc123"
    m2 = u("a", "b", "c").closure()
    self.assertFalse(matches(m1, m2))


class PyniniPdtReplaceTest(unittest.TestCase):

  def testPdtReplace(self):
    s_rhs = union("a[S]b", "ab")  # a^n b^n.
    (f, parens) = pdt_replace("[S]", (("S", s_rhs),))
    for n in xrange(1, 100):
      anbn = n * "a" + n * "b"
      self.assertEqual(pdt_compose(f, anbn, parens, compose_filter="expand"),
                       anbn)


class PyniniReplaceTest(unittest.TestCase):

  # Based loosely on an example from Thrax.

  def testReplace(self):
    root = acceptor("[Number] [Measure]")
    singular_numbers = transducer("1", "one")
    singular_measurements = string_map(
        (("ft", "foot"), ("in", "inch"), ("cm", "centimeter"), ("m", "meter"),
         ("kg", "kilogram")))
    singular = replace(
        root, (("Number", singular_numbers), ("Measure",
                                              singular_measurements)),
        call_arc_labeling="neither",
        return_arc_labeling="neither")
    self.assertEqual(optimize(project("1 ft" * singular, True)), "one foot")
    plural_numbers = string_map(
        (("2", "two"), ("3", "three"), ("4", "four"), ("5", "five"),
         ("6", "six"), ("7", "seven"), ("8", "eight"), ("9", "nine")))
    plural_measurements = string_map(
        (("ft", "feet"), ("in", "inches"), ("cm", "centimeter"),
         ("m", "meters"), ("kg", "kilograms")))
    plural = replace(
        root, (("Number", plural_numbers), ("Measure", plural_measurements)),
        call_arc_labeling="neither",
        return_arc_labeling="neither")
    self.assertEqual(optimize(project("2 m" * plural, True)), "two meters")

  def testReplaceWithCyclicDependenciesRaisesFstOpError(self):
    s_rhs = union("a[S]b", "ab")  # a^n b^n.
    with self.assertRaises(FstOpError):
      unused_f = replace("[S]", (("S", s_rhs),))


class PyniniStringTest(unittest.TestCase):

  """Tests string compilation and stringification."""

  @classmethod
  def setUpClass(cls):
    cls.cheese = b"Red Leicester"
    cls.reply = b"I'm afraid we're fresh out of Red Leicester sir"
    cls.imported_cheese = u"Pont l'Evêque"
    cls.imported_cheese_encoded = cls.imported_cheese.encode("utf8")
    cls.acceptor_props = (ACCEPTOR | I_DETERMINISTIC | O_DETERMINISTIC |
                          I_LABEL_SORTED | O_LABEL_SORTED | UNWEIGHTED |
                          ACYCLIC | INITIAL_ACYCLIC | TOP_SORTED | ACCESSIBLE |
                          COACCESSIBLE | STRING | UNWEIGHTED_CYCLES)

  def testUnbracketedBytestringUnweightedAcceptorCompilation(self):
    cheese = acceptor(self.cheese)
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testUnbracketedBytestringUnweightedTransducerCompilation(self):
    exchange = transducer(self.cheese, self.reply)
    exchange.project()
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testUnbracketedBytestringWeightedAcceptorCompilation(self):
    cheese = acceptor(self.cheese, weight=Weight.One("tropical"))
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testUnbracketedBytestringWeightedTransducerCompilation(self):
    exchange = transducer(self.cheese, self.reply,
                          weight=Weight.One("tropical"))
    exchange.project()
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testUnbracketedBytestringCastingWeightedAcceptorCompilation(self):
    cheese = acceptor(self.cheese, weight=0)
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testBracketedTokenizationAcceptorCompilation(self):
    cheese_tokens = self.cheese.split()
    cheese = acceptor("".join("[{}]".format(t) for t in cheese_tokens))
    i = cheese.input_symbols().find(cheese_tokens[1])  # "Leicester".
    self.assertGreater(i, 255)

  def testBracketedCharsBytestringAcceptorCompilation(self):
    cheese = acceptor("".join("[{:d}]".format(ord(ch)) for ch in self.cheese))
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testUnicodeBytestringAcceptorCompilation(self):
    cheese = acceptor(self.imported_cheese)
    self.assertEqual(cheese, self.imported_cheese.encode("utf8"))
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testAsciiUtf8AcceptorCompilation(self):
    cheese = acceptor(self.cheese, token_type="utf8")
    self.assertEqual(cheese, self.cheese)
    self.assertEqual(cheese.properties(self.acceptor_props, True),
                     self.acceptor_props)

  def testUnicodeUtf8AcceptorCompilation(self):
    cheese = acceptor(self.imported_cheese, token_type="utf8")
    for (i, state) in enumerate(cheese.states()):
      for arc in cheese.arcs(state):
        self.assertEqual(unichr(arc.olabel), self.imported_cheese[i])

  def testEscapedBracketsBytestringAcceptorCompilation(self):
    ac = acceptor("[\[Camembert\] is a]\[cheese\]")
    self.assertEqual(ac.num_states(), 12)
    # Should have 3 states accepting generated symbols, 8 accepting a byte,
    # and 1 final state.

  def testGarbageWeightAcceptorRaisesFstBadWeightError(self):
    with self.assertRaises(FstBadWeightError):
      unused_ac = acceptor(self.cheese, weight="nonexistent")

  def testGarbageWeightTransducerRaisesFstBadWeightError(self):
    with self.assertRaises(FstBadWeightError):
      unused_tr = transducer(self.cheese, self.reply, weight="nonexistent")

  def testGarbageArcTypeAcceptorRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_ac = acceptor(self.cheese, arc_type="nonexistent")

  def testGarbageArcTypeTransducerRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_tr = transducer(self.cheese, self.reply, arc_type="nonexistent")

  def testUnbalancedBracketsAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstStringCompilationError):
      unused_ac = acceptor(self.cheese + "]")

  def testUnbalancedBracketsTransducerRaisesFstStringCompilationError(self):
    with self.assertRaises(FstStringCompilationError):
      unused_tr = transducer(self.cheese, "[" + self.reply)

  def testCrossProductTransducerCompilation(self):
    cheese = acceptor(self.cheese)
    reply = acceptor(self.reply)
    exchange = transducer(cheese, reply)
    exchange.project()
    exchange.rmepsilon()
    self.assertEqual(exchange, self.cheese)

  def testAsciiByteStringify(self):
    self.assertEqual(acceptor(self.cheese).stringify(), self.cheese)

  def testAsciiUtf8Stringify(self):
    self.assertEqual(acceptor(self.cheese, token_type="utf8").stringify("utf8"),
                     self.cheese)

  def testUtf8ByteStringify(self):
    self.assertEqual(acceptor(self.imported_cheese_encoded).stringify(),
                     self.imported_cheese_encoded)

  def testAsciiByteStringifyAfterSymbolTableDeletion(self):
    ac = acceptor(self.cheese)
    ac.set_output_symbols(None)
    self.assertEqual(ac.stringify(), self.cheese)

  def testUtf8Utf8Stringify(self):
    self.assertEqual(acceptor(self.imported_cheese_encoded,
                              token_type="utf8").stringify("utf8"),
                     self.imported_cheese_encoded)

  def testUnicodeByteStringify(self):
    self.assertEqual(acceptor(self.imported_cheese).stringify(),
                     self.imported_cheese_encoded)

  def testUnicodeUtf8Stringify(self):
    self.assertEqual(acceptor(self.imported_cheese,
                              token_type="utf8").stringify("utf8"),
                     self.imported_cheese_encoded)

  def testUtf8StringifyAfterSymbolTableDeletion(self):
    ac = acceptor(self.imported_cheese, token_type="utf8")
    ac.set_output_symbols(None)
    self.assertEqual(ac.stringify("utf8"), self.imported_cheese_encoded)

  def testUnicodeSymbolStringify(self):
    ac = acceptor(self.imported_cheese, token_type="utf8")
    self.assertEqual(ac.stringify(ac.output_symbols()),
                     b"P o n t <SPACE> l ' E v <0xea> q u e")

  def testStringifyOnNonkStringFstRaisesFstArgError(self):
    with self.assertRaises(FstArgError):
      unused_ac = union(self.cheese, self.imported_cheese).stringify()

  def testCompositionOfStringAndLogArcWorks(self):
    cheese = "Greek Feta"
    self.assertEqual(cheese * acceptor(cheese, arc_type="log"), cheese)

  def testCompositionOfLogArcAndStringWorks(self):
    cheese = "Tilsit"
    self.assertEqual(acceptor(cheese, arc_type="log") * cheese, cheese)

  def testCompositionOfStringAndLog64ArcWorks(self):
    cheese = "Greek Feta"
    self.assertEqual(cheese * acceptor(cheese, arc_type="log64"), cheese)

  def testCompositionOfLog64ArcAndStringWorks(self):
    cheese = "Tilsit"
    self.assertEqual(acceptor(cheese, arc_type="log64") * cheese, cheese)

  def testLogWeightToStandardAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstOpError):
      unused_ac = acceptor("Sage Derby", weight=Weight.One("log"))

  def testLog64WeightToLogAcceptorRaisesFstStringCompilationError(self):
    with self.assertRaises(FstOpError):
      unused_ac = acceptor("Wensleydale", arc_type="log",
                           weight=Weight.One("log64"))

  def testTropicalWeightToLog64TransducerRaisesFstOpError(self):
    with self.assertRaises(FstOpError):
      unused_tr = transducer("Venezuelan Beaver Cheese", "Not today sir, no",
                             arc_type="log64", weight=Weight.One("tropical"))


class PyniniStringFileTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.map_file =  "testdata/cheese.map"

  def testByteToByteStringFile(self):
    mapper = string_file(self.map_file)
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     "Pont-l'Évêque")
    self.assertEqual(optimize(project("Pont-l'Évêque" * mapper, True)),
                     "Camembert")

  def testByteToUtf8StringFile(self):
    mapper = string_file(self.map_file, output_token_type="utf8")
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     acceptor("Pont-l'Évêque", token_type="utf8"))
    self.assertEqual(optimize(project("Pont-l'Évêque" * mapper, True)),
                     "Camembert")

  def testUtf8ToUtf8StringFile(self):
    mapper = string_file(self.map_file, input_token_type="utf8",
                         output_token_type="utf8")
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     acceptor("Pont-l'Évêque", token_type="utf8"))
    self.assertEqual(optimize(project(acceptor("Pont-l'Évêque",
                                               token_type="utf8") * mapper,
                                      True)),
                     "Camembert")

  def testByteToSymbolStringFile(self):
    syms = SymbolTable()
    syms.add_symbol("<epsilon>")
    syms.add_symbol("Sorry")
    syms.add_symbol("Cheddar")
    syms.add_symbol("Pont-l'Évêque")
    syms.add_symbol("Camembert")
    mapper = string_file(self.map_file, output_token_type=syms)
    sorry = acceptor("Sorry", token_type=syms)
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), sorry)
    cheddar = acceptor("Cheddar", token_type=syms)
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), cheddar)
    pont_levesque = acceptor("Pont-l'Évêque", token_type=syms)
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     pont_levesque)


class PyniniStringMapTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.pairs = (("[Bel Paese]", "Sorry"), ("Cheddar",),
                 ("Caithness", "Pont-l'Évêque"),
                 ("Pont-l'Évêque", "Camembert"))

  def testHeterogeneousStringMap(self):
    mapper = string_map([self.pairs[0],   # Tuple.
                         self.pairs[1]])  # String.
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")

  def testByteToByteStringMap(self):
    mapper = string_map(self.pairs)
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     "Pont-l'Évêque")
    self.assertEqual(optimize(project("Pont-l'Évêque" * mapper, True)),
                     "Camembert")

  def testDictionaryStringMap(self):
    mydict = {self.pairs[0][0]: self.pairs[0][1],
              self.pairs[1][0]: self.pairs[1][0]}
    mapper = string_map(mydict)
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")

  def testByteToUtf8StringMap(self):
    mapper = string_map(self.pairs, output_token_type="utf8")
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     acceptor("Pont-l'Évêque", token_type="utf8"))
    self.assertEqual(optimize(project("Pont-l'Évêque" * mapper, True)),
                     "Camembert")

  def testUtf8ToUtf8StringMap(self):
    mapper = string_map(self.pairs, input_token_type="utf8",
                        output_token_type="utf8")
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), "Sorry")
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), "Cheddar")
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     acceptor("Pont-l'Évêque", token_type="utf8"))
    self.assertEqual(optimize(project(acceptor("Pont-l'Évêque",
                                               token_type="utf8") * mapper,
                                      True)),
                     "Camembert")

  def testByteToSymbolStringMap(self):
    syms = SymbolTable()
    syms.add_symbol("<epsilon>")
    syms.add_symbol("Sorry")
    syms.add_symbol("Cheddar")
    syms.add_symbol("Pont-l'Évêque")
    syms.add_symbol("Camembert")
    mapper = string_map(self.pairs, output_token_type=syms)
    sorry = acceptor("Sorry", token_type=syms)
    self.assertEqual(optimize(project("[Bel Paese]" * mapper, True)), sorry)
    cheddar = acceptor("Cheddar", token_type=syms)
    self.assertEqual(optimize(project("Cheddar" * mapper, True)), cheddar)
    pont_levesque = acceptor("Pont-l'Évêque", token_type=syms)
    self.assertEqual(optimize(project("Caithness" * mapper, True)),
                     pont_levesque)


class PyniniStringPathsTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.triples = (("Bel Paese", "Sorry", Weight("tropical", 4.)),
                   ("Red Windsor",
                    "Normally, sir, yes, but today the van broke down.",
                    Weight("tropical", 3.)),
                   ("Stilton", "Sorry", Weight("tropical", 2.)))
    cls.f = union(*(transducer(*triple) for triple in cls.triples))

  def testStringPaths(self):
    for (triple, triple_res) in zip(self.f.paths(), self.triples):
      self.assertEqual(triple_res, triple)

  def testStringPathsIterIStrings(self):
    self.assertItemsEqual(self.f.paths().iter_istrings(),
                          (t[0] for t in self.triples))

  def testStringPathsIterOStrings(self):
    self.assertItemsEqual(self.f.paths().iter_ostrings(),
                          (t[1] for t in self.triples))

  def testStringPathsIterWeights(self):
    self.assertItemsEqual((str(w) for w in self.f.paths().iter_weights()),
                          (str(t[2]) for t in self.triples))

  def testStringPathsAfterFstDeletion(self):
    f = u("Pipo Crem'", "Fynbo")
    sp = StringPaths(f)
    del f   # Should be garbage-collected immediately.
    self.assertEqual(len(list(sp)), 2)

  def testStringPathLabelsWithoutEpsilons(self):
    cheese = "Cheddar"
    f = a(cheese)
    chars = [ord(i) for i in cheese]
    sp = StringPaths(f)
    eps_free_ilabels = sp.ilabels()
    self.assertEqual(eps_free_ilabels, chars)
    self.assertEqual(sp.ilabels(), eps_free_ilabels)
    eps_free_olabels = sp.olabels()
    self.assertEqual(eps_free_olabels, eps_free_ilabels)
    self.assertEqual(sp.olabels(), eps_free_olabels)
    sp.next()
    self.assertTrue(sp.done())

  def testStringPathLabelsWithEpsilons(self):
    # Note that the Thompson construction for union connects the initial state
    # of the first FST to the initial state of the second FST with an
    # epsilon-arc, a fact we take advantage of here.
    f = u("Ilchester", "Limburger")
    sp = StringPaths(f)
    self.assertEqual(sp.ilabels(), sp.ilabels())
    sp.next()
    self.assertEqual(sp.ilabels(), sp.ilabels())
    sp.next()
    self.assertTrue(sp.done())


class PyniniSymbolTableTest(unittest.TestCase):

  def testInputSymbolTableAccessAfterFstDeletion(self):
    f = transducer("Greek Feta", "Ah, not as such")
    isyms = f.input_symbols().copy()
    isyms2 = f.input_symbols()
    del f  # Should be garbage-collected immediately.
    self.assertEqual(isyms2.labeled_checksum(), isyms.labeled_checksum())

  def testOutputSymbolTableAccessAfterFstDeletion(self):
    f = transducer("Red Windsor", "Normally, sir, yes, "
                                  "but today the van broke down")
    osyms = f.output_symbols().copy()
    osyms2 = f.output_symbols()
    del f  # Should be garbage-collected immediately.
    self.assertEqual(osyms2.labeled_checksum(), osyms.labeled_checksum())


class PyniniWeightTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    half = -math.log(.5)
    one_half = -math.log(1.5)
    two = -math.log(2)
    cls.delta = 1. / 1024.
    cls.tropical_zero = Weight.Zero("tropical")
    cls.tropical_half = Weight("tropical", half)
    cls.tropical_one = Weight.One("tropical")
    cls.log_zero = Weight.Zero("log")
    cls.log_half = Weight("log", half)
    cls.log_one = Weight.One("log")
    cls.log_one_half = Weight("log", one_half)
    cls.log_two = Weight("log", two)
    cls.log64_zero = Weight.Zero("log64")
    cls.log64_half = Weight("log64", half)
    cls.log64_one = Weight.One("log64")
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


class PyniniWorkedExampleTest(unittest.TestCase):

  def testWorkedExample(self):
    pairs = zip(string.ascii_lowercase, string.ascii_uppercase)
    self.upcaser = string_map(pairs).closure()
    self.downcaser = invert(self.upcaser)
    awords = "You do have some cheese do you".lower().split()
    for aword in awords:
      result = (aword * self.upcaser).project(True).optimize()
      self.assertEqual(result, aword.upper())
    cheese = "Parmesan".lower()
    cascade = (cheese * self.upcaser * self.downcaser *
               self.upcaser * self.downcaser)
    self.assertEqual(cascade.stringify(), cheese)


def main():
  unittest.main()


if __name__ == "__main__":
  main()
