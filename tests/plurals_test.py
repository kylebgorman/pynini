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
"""Tests of English plurals."""

from pynini.examples import plurals

from absl.testing import absltest


class EnglishPluralsTest(absltest.TestCase):

  def assertPlural(self, singular: str, plural: str):
    result = plurals.plural(singular)
    self.assertEqual(result, plural)

  def testPlurals(self):
    self.assertPlural("analysis", "analyses")
    self.assertPlural("boy", "boys")
    self.assertPlural("deer", "deer")
    self.assertPlural("hamlet", "hamlets")
    self.assertPlural("house", "houses")
    self.assertPlural("lunch", "lunches")
    self.assertPlural("mouse", "mice")
    self.assertPlural("photo", "photos")
    self.assertPlural("puppy", "puppies")
    self.assertPlural("wife", "wives")


if __name__ == "__main__":
  absltest.main()

