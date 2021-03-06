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

"""Tests for multi_grm."""

import os

from absl import flags
from absl.testing import flagsaver

import pynini
from pynini.export import multi_grm
from absl.testing import absltest


FLAGS = flags.FLAGS


def generator_method(exporter_map: multi_grm.ExporterMapping):
  exporter_a = exporter_map['a']
  exporter_a['FST1'] = pynini.accep('1234')
  exporter_b = exporter_map['b']
  exporter_b['FST2'] = pynini.accep('4321')
  exporter_b['FST3'] = pynini.accep('ABCD')


def _read_fst_map(filename):
  with pynini.Far(filename) as far:
    stored_fsts = dict(far)
  return stored_fsts


class PyniniMultiGrmTest(absltest.TestCase):

  @flagsaver.flagsaver()
  def testFilledExporter(self):
    """Export two FARs and check that they contain the right FSTs."""
    filename_a = os.path.join(FLAGS.test_tmpdir, 'test_a.far')
    filename_b = os.path.join(FLAGS.test_tmpdir, 'test_b.far')
    FLAGS.outputs = 'a=' + filename_a + ',b=' + filename_b
    with self.assertRaises(SystemExit):
      multi_grm.run(generator_method)

    stored_fsts_a = _read_fst_map(filename_a)
    self.assertLen(stored_fsts_a, 1)
    self.assertTrue(stored_fsts_a['FST1'])

    stored_fsts_b = _read_fst_map(filename_b)
    self.assertLen(stored_fsts_b, 2)
    self.assertTrue(stored_fsts_b['FST2'])
    self.assertTrue(stored_fsts_b['FST3'])


if __name__ == '__main__':
  absltest.main()

