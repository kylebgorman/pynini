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
"""Tests for the T9 model."""


from pynini.examples import t9
from absl.testing import absltest


class T9Test(absltest.TestCase):

  t9: t9.T9

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    lexicon = [
        "the", "cool", "warthog", "escaped", "easily", "from", "baltimore",
        "zoo", "col"
    ]
    cls.t9 = t9.T9(lexicon)

  def testExample(self):
    example = "the cool warthog escaped easily from baltimore zoo"
    encoded = self.t9.encode(example)
    self.assertTrue(example in self.t9.decode(encoded).paths().ostrings())


if __name__ == "__main__":
  absltest.main()

