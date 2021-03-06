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
"""Tests of the tagger automaton class."""

import string

from absl.testing import absltest

import pynini
from pynini.lib import rewrite
from pynini.lib import tagger


class TaggerTest(absltest.TestCase):

  tagger: tagger.Tagger

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cheese = pynini.string_map([
        "tilsit", "caerphilly", "stilton", "gruyere", "emmental", "liptauer",
        "lancashire", "cheshire", "brie", "roquefort", "savoyard", "boursin",
        "camembert", "gouda", "edam", "caithness", "wensleydale", "gorgonzola",
        "parmesan", "mozzarella", "fynbo", "cheddar", "ilchester", "limburger"
    ]).optimize()
    sigma_star = pynini.union(*string.ascii_lowercase + "<>/ ").closure()
    cls.tagger = tagger.Tagger("cheese", cheese, sigma_star)

  def testMatch(self):
    request = "well how about cheddar"
    self.assertEqual(
        self.tagger.tag(request), "well how about <cheese>cheddar</cheese>")

  def testMatches(self):
    request = "do you have tilsit caerphilly gruyere emmental or edam"
    self.assertEqual(
        self.tagger.tag(request), "do you have <cheese>tilsit</cheese> "
        "<cheese>caerphilly</cheese> "
        "<cheese>gruyere</cheese> "
        "<cheese>emmental</cheese> or "
        "<cheese>edam</cheese>")

  def testOutofAlphabetQueryRaisesException(self):
    request = "Gruyère"
    with self.assertRaises(rewrite.Error):
      self.tagger.tag(request)


if __name__ == "__main__":
  absltest.main()

