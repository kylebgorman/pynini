# Copyright 2016-2024 Google LLC
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
"""Tests for the automatic stringfile creation utility."""

import io

import logging

import pynini
from pynini.lib import stringfile
from absl.testing import absltest


class StringfileEscapeTest(absltest.TestCase):

  def test_empty_string(self):
    self.assertEqual(stringfile.escape(""), "")

  def test_non_special_chars(self):
    self.assertEqual(stringfile.escape(r"abc"), r"abc")

  def test_brackets(self):
    self.assertEqual(stringfile.escape(r"[abc]"), r"\[abc\]")

  def test_backslash(self):
    self.assertEqual(stringfile.escape("a\\slash\\"), "a\\\\slash\\\\")

  def test_hashtag(self):
    self.assertEqual(stringfile.escape(r"#awesome"), r"\#awesome")

  def test_escaped_backslash_before_hashtag(self):
    self.assertEqual(stringfile.escape("\\\\#"), "\\\\\\\\\\#")

  def test_unescaped_backslash_before_hashtag(self):
    self.assertEqual(stringfile.escape("\\#"), "\\\\\\#")


class StringfileWriteTest(absltest.TestCase):

  def test_write_line(self):
    with io.StringIO() as f:
      stringfile.writeline(f, ["#awesome", "#lo mejor", "4"])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 1)
      self.assertEqual(lines[0], "\\#awesome\t\\#lo mejor\t4\n")

  def test_too_few_fields(self):
    with io.StringIO() as f:
      with self.assertLogs(level=logging.ERROR):
        stringfile.writeline(f, [])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 1)
      self.assertEqual(lines[0], "\n")

  def test_too_many_fields(self):
    with io.StringIO() as f:
      with self.assertLogs(level=logging.ERROR):
        stringfile.writeline(f, ["#awesome", "#lo mejor", "4", "too many"])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 1)
      self.assertEqual(lines[0], "\\#awesome\t\\#lo mejor\t4\ttoo many\n")

  def test_write_two_column_line(self):
    with io.StringIO() as f:
      stringfile.writeline(f, ["#awesome", "#lo mejor"])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 1)
      self.assertEqual(lines[0], "\\#awesome\t\\#lo mejor\n")

  def test_write_one_column_line(self):
    with io.StringIO() as f:
      stringfile.writeline(f, ["#awesome"])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 1)
      self.assertEqual(lines[0], "\\#awesome\n")

  def test_write_lines(self):
    with io.StringIO() as f:
      stringfile.writelines(f, [("#awesome", "#lo mejor", "4"),
                                ("[bracketed]", "סוגריים מרובעים", "5")])
      f.seek(0)
      lines = f.readlines()
      self.assertLen(lines, 2)
      self.assertEqual(lines[0], "\\#awesome\t\\#lo mejor\t4\n")
      self.assertEqual(lines[1], "\\[bracketed\\]\tסוגריים מרובעים\t5\n")

  def test_roundtrip(self):
    lines = [("#awesome", "#lo mejor", "4"),
             ("[bracketed]", "סוגריים מרובעים", "5"),
             ("\\\\#", "words", "0")]
    temp = self.create_tempfile()
    with temp.open_text("wt") as f:
      stringfile.writelines(f, lines)

    fst = pynini.string_file(temp.full_path)
    self.assertEqual(lines,
                     [(istring, ostring, str(weight))
                      for istring, ostring, weight in fst.paths().items()])


if __name__ == "__main__":
  absltest.main()

