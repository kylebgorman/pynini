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
"""Tests of Spanish g2p rules."""

from pynini.examples import g2p

from absl.testing import absltest


class SpanishG2PTest(absltest.TestCase):

  def assertPron(self, grapheme: str, phoneme: str):
    self.assertEqual(g2p.g2p(grapheme), phoneme)

  def testG2P(self):
    self.assertPron("anarquista", "anarkista")
    self.assertPron("cantar", "kantar")
    self.assertPron("gañir", "gaɲir")
    self.assertPron("hacer", "aser")
    self.assertPron("hijo", "ixo")
    self.assertPron("llave", "ʝabe")
    self.assertPron("pero", "peɾo")
    self.assertPron("perro", "pero")
    self.assertPron("vivir", "bibir")


if __name__ == "__main__":
  absltest.main()

