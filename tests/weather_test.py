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
"""Tests for the weather generator."""

from absl.testing import absltest

from pynini.examples import weather


class WeatherTest(absltest.TestCase):

  weather_table: weather.WeatherTable

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.weather_table = weather.WeatherTable()
    cls.weather_table.add_city("London", 1, 3, "northwest", "cloudy")
    cls.weather_table.add_city("New York", 15, 1, "southeast", "overcast")

  def testGenerateReport(self):
    self.assertEqual(
        self.weather_table.generate_report("New York"),
        ("In New York, it is 15 degrees and overcast, with winds out of the "
         "southeast at 1 kilometer per hour."))
    self.assertEqual(
        self.weather_table.generate_report("London"),
        ("In London, it is 1 degree and cloudy, with winds out of the "
         "northwest at 3 kilometers per hour."))


if __name__ == "__main__":
  absltest.main()

