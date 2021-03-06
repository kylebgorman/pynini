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

"""Tests for grm."""

import os

from absl import flags
from absl.testing import flagsaver

import pynini
from pynini.export import grm
from absl.testing import absltest


FLAGS = flags.FLAGS


def generator_method(exporter: grm.Exporter):
  exporter['FST1'] = pynini.accep('1234')
  exporter['FST2'] = pynini.accep('4321')


class PyniniGrmTest(absltest.TestCase):

  @flagsaver.flagsaver()
  def testFilledExporter(self):
    """Export two FSTs and check that they are stored in the file."""
    filename = os.path.join(FLAGS.test_tmpdir, 'test.far')
    FLAGS.output = filename
    with self.assertRaises(SystemExit):
      grm.run(generator_method)
    with pynini.Far(filename, 'r') as far:
      stored_fsts = dict(far)
    self.assertLen(stored_fsts, 2)
    self.assertTrue(stored_fsts['FST1'])
    self.assertTrue(stored_fsts['FST2'])


if __name__ == '__main__':
  absltest.main()

