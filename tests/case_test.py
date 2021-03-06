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
"""Tests of Finnish case suffixes."""

from pynini.examples import case

from absl.testing import absltest


class FinnishCaseTest(absltest.TestCase):

  def assertCases(self, nominative: str, abessive: str, ablative: str,
                  adessive: str, allative: str, elative: str, essive: str,
                  inessive: str):
    self.assertEqual(case.abessive(nominative), abessive)
    self.assertEqual(case.ablative(nominative), ablative)
    self.assertEqual(case.adessive(nominative), adessive)
    self.assertEqual(case.allative(nominative), allative)
    self.assertEqual(case.elative(nominative), elative)
    self.assertEqual(case.essive(nominative), essive)
    self.assertEqual(case.inessive(nominative), inessive)

  def testBackHarmonicStems(self):
    # Back-back: 'house'; https://en.wiktionary.org/wiki/talo#Finnish
    self.assertCases("talo", "talotta", "talolta", "talolla", "talolle",
                     "talosta", "talona", "talossa")
    # Front-back: 'cyst'; https://en.wiktionary.org/wiki/kysta#Finnish
    self.assertCases("kysta", "kystatta", "kystalta", "kystalla", "kystalle",
                     "kystasta", "kystana", "kystassa")
    # Back-neutral: 'sailor'; https://en.wiktionary.org/wiki/gasti#Finnish
    self.assertCases("gasti", "gastitta", "gastilta", "gastilla", "gastille",
                     "gastista", "gastina", "gastissa")
    # Neutral-back: 'tax': https://en.wiktionary.org/wiki/vero#Finnish
    self.assertCases("vero", "verotta", "verolta", "verolla", "verolle",
                     "verosta", "verona", "verossa")

  def testFrontHarmonicStems(self):
    # Back-front: 'fondue'; https://en.wiktionary.org/wiki/fondyy#Finnish
    self.assertCases("fondyy", "fondyyttä", "fondyyltä", "fondyyllä",
                     "fondyylle", "fondyystä", "fondyynä", "fondyyssä")
    # Front-front: 'spit'; https://en.wiktionary.org/wiki/sylky#Finnish
    self.assertCases("sylky", "sylkyttä", "sylkyltä", "sylkyllä", "sylkylle",
                     "sylkystä", "sylkynä", "sylkyssä")
    # Neutral-neutral: 'pleat'; https://en.wiktionary.org/wiki/vekki#Finnish
    self.assertCases("vekki", "vekkittä", "vekkiltä", "vekkillä", "vekkille",
                     "vekkistä", "vekkinä", "vekkissä")


if __name__ == "__main__":
  absltest.main()

