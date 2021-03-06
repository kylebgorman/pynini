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
"""Tests of (American) English number names."""

from pynini.examples import numbers

from absl.testing import absltest


class EnNumbersTest(absltest.TestCase):

  def test_rewrites(self):
    pairs = [
        (324, "three hundred twenty four"),
        (314, "three hundred fourteen"),  # Forcing newline.
        (3014, "three thousand fourteen"),
        (30014, "thirty thousand fourteen"),
        (300014, "three hundred thousand fourteen"),
        (3000014, "three million fourteen")
    ]
    for (number, name) in pairs:
      prediction = numbers.number(str(number))
      self.assertEqual(name, prediction, f"{name} != {prediction}")


if __name__ == "__main__":
  absltest.main()

