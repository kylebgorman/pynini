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
"""Tests for the Date extractor."""

import functools

from absl.testing import absltest

from pynini.examples import dates


class DatesTest(absltest.TestCase):

  def testDateCardinal(self):
    self.assertEqual(
        dates.match("January 2, 1985"),
        "<date><month>1</month><day>2</day><year>1985</year></date>")

  def testDateOrdinal(self):
    self.assertEqual(
        dates.match("January the 2nd, 1985"),
        "<date><month>1</month><day>2</day><year>1985</year></date>")

  def testInvertedDateCardinal(self):
    self.assertEqual(
        dates.match("2 January, 1985"),
        "<date><day>2</day><month>1</month><year>1985</year></date>")

  def testInvertedDateOrdinal(self):
    self.assertEqual(
        dates.match("the 2nd of January, 1985"),
        "<date><day>2</day><month>1</month><year>1985</year></date>")

  def testYMD(self):
    self.assertEqual(
        dates.match("1985/1/2"),
        "<date><year>1985</year><month>1</month><day>2</day></date>")

  def testDMY(self):
    self.assertEqual(
        dates.match("2/1/1985"),
        "<date><day>2</day><month>1</month><year>1985</year></date>")

  def testTagger(self):
    text = "I met John on June 1, 1985 in Colorado."
    expected = ("I met John on <date><month>6</month><day>1</day>"
                "<year>1985</year></date> in Colorado.")
    self.assertEqual(dates.tag(text), expected)

  def testTaggerLong(self):
    """Tests extraction on an excerpt from Wikipedia.

    Excerpt from https://en.wikipedia.org/wiki/Winston_Churchill,
    accesssed 2019-11-08.
    """
    text = """Churchill was born at the family's ancestral home,
Blenheim Palace in Oxfordshire, on 30 November 1874,
at which time the United Kingdom was the dominant world power.
Direct descendants of the Dukes of Marlborough, his family were
among the highest levels of the British aristocracy, and thus
he was born into the country's governing elite.
His paternal grandfather, John Spencer-Churchill,
7th Duke of Marlborough, had been a Member of Parliament (MP)
for ten years, a member of the Conservative Party who served
in the government of Prime Minister Benjamin Disraeli.
His own father, Lord Randolph Churchill, had been elected
Conservative MP for Woodstock in 1873.
His mother, Jennie Churchill (née Jerome), was from an
American family whose substantial wealth derived from
finance. The couple had met in August 1873, and were
engaged three days later, marrying at the British Embassy
in Paris in April 1874. The couple lived beyond their income
and were frequently in debt; according to the biographer
Sebastian Haffner, the family were "rich by normal
standards but poor by those of the rich".""".replace("\n", " ")
    # Note that the model does not handle the case of year alone (e.g. "1873")
    # since that can easily overgenerate. One would want to build a more
    # sophisticated classifier to handle such cases.
    result = dates.tag(text)
    self.assertIn(
        "<date><day>30</day><month>11</month><year>1874</year></date>", result)
    self.assertIn("<date><month>8</month><year>1873</year></date>", result)
    self.assertIn("<date><month>4</month><year>1874</year></date>", result)


if __name__ == "__main__":
  absltest.main()

