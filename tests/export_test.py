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

"""Tests for exporter."""

import os

from absl import flags

import pynini
from pynini.export import export
from absl.testing import absltest

FLAGS = flags.FLAGS


def _read_fst_map(filename):
  with pynini.Far(filename) as far:
    stored_fsts = dict(far)
  return stored_fsts


class PyniniExporterTest(absltest.TestCase):
  _filename: str

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls._filename = os.path.join(FLAGS.test_tmpdir, 'test.far')

  def testEmptyExporter(self):
    """Export an empty grammar."""
    exporter = export.Exporter(self._filename)
    exporter.close()
    self.assertTrue(os.path.isfile(self._filename))

  def testFilledExporter(self):
    """Export two FSTs."""
    exporter = export.Exporter(self._filename)
    exporter['FST1'] = pynini.accep('1234')
    exporter['FST2'] = pynini.accep('4321')
    exporter.close()
    stored_fsts = _read_fst_map(self._filename)
    self.assertLen(stored_fsts, 2)
    self.assertTrue(stored_fsts['FST1'])
    self.assertTrue(stored_fsts['FST2'])

  def testFilledExporterWithFarTypes(self):
    """Export two FSTs different far types."""
    for far_type in ['default',  'sttable', 'stlist']:
      # TODO(b/123775699): Currently pytype thinks `export.Exporter.__init__`'s
      # `far_type` arg expects Any here, but inside `__init__` itself, it
      # correctly expects the `Literal` type, `pynini.FarType`. This silences
      # what could have been an error: its labeling `far_type` as type `str`
      # though it is guaranteed to take values of type `pynini.FarType`.
      exporter = export.Exporter(self._filename, far_type=far_type)
      exporter['FSTA'] = pynini.accep('1234')
      exporter['FSTB'] = pynini.accep('4321')
      exporter.close()
      stored_fsts = _read_fst_map(self._filename)
      self.assertLen(stored_fsts, 2)
      self.assertTrue(stored_fsts['FSTA'])
      self.assertTrue(stored_fsts['FSTB'])

if __name__ == '__main__':
  absltest.main()

