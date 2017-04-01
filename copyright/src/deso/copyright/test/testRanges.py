#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015-2016 Daniel Mueller (deso@posteo.net)              *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************/

"""A test suite for the range sequence handling functionality."""

from deso.copyright import (
  normalizeRanges,
  parseRanges,
  Range,
)
from unittest import (
  main,
  TestCase,
)


class TestRanges(TestCase):
  """Tests for the range sequence handling functionality."""
  def testNormalizeRanges(self):
    """Test normalizing of lists of ranges."""
    def doTest(ranges, expected):
      """Verify that a normalization produces the expected ranges."""
      normalizeRanges(ranges)
      self.assertEqual(ranges, expected)

    # Merging of a single range should be trivial.
    doTest([Range(2014, 2014)], [Range(2014, 2014)])

    # Merging of two ranges into a single.
    doTest([Range(2014, 2015), Range(2014, 2014)], [Range(2014, 2015)])
    doTest([Range(2014, 2015), Range(2013, 2013)], [Range(2013, 2015)])
    doTest([Range(2013, 2014), Range(2015, 2015)], [Range(2013, 2015)])

    # Merging of three ranges into a single.
    doTest([Range(2014, 2014),
            Range(2014, 2014),
            Range(2014, 2014)], [Range(2014, 2014)])
    doTest([Range(2013, 2015),
            Range(2010, 2010),
            Range(2011, 2012)], [Range(2010, 2015)])
    doTest([Range(2013, 2013),
            Range(2012, 2012),
            Range(1995, 2014)], [Range(1995, 2014)])

    # All sorts of merges (hopefully) with more ranges involved or as a
    # result.
    doTest([Range(2010, 2011),
            Range(2012, 2013),
            Range(2015, 2015)], [Range(2010, 2013), Range(2015, 2015)])

    ranges = [Range(2015, 2015),
              Range(2010, 2011),
              Range(2013, 2013)]
    expected = [Range(2010, 2011),
                Range(2013, 2013),
                Range(2015, 2015)]
    doTest(ranges, expected)

    doTest([Range(2013, 2013),
            Range(2012, 2012),
            Range(1995, 2014),
            Range(2015, 2015)], [Range(1995, 2015)])


  def testParseRanges(self):
    """Test the parsing functionality for sequences of ranges."""
    def doTest(rangesString, expected):
      """Parse a string of ranges and compare the results against the expected one."""
      ranges = parseRanges(rangesString)
      self.assertEqual(ranges, expected)

    doTest("2015", [Range(2015, 2015)])
    doTest("2014 -2015", [Range(2014, 2015)])
    doTest("2013- 2015", [Range(2013, 2015)])
    doTest("2012-2015", [Range(2012, 2015)])
    doTest("2014,2015", [Range(2014, 2014), Range(2015, 2015)])
    doTest("2013 , \t2015", [Range(2013, 2013), Range(2015, 2015)])
    doTest("2015, 2013,2014 ", [Range(2015, 2015),
                                Range(2013, 2013),
                                Range(2014, 2014)])
    doTest("2013-2015,2011-2013", [Range(2013, 2015), Range(2011, 2013)])
    # A trailing separator should just be ignored.
    doTest("2011-2012,", [Range(2011, 2012)])


  def testParseRangesFailures(self):
    """Negative test for the range sequence parsing functionality."""
    def doTest(rangesString):
      """Check that parsing invalid ranges causes expected failures."""
      with self.assertRaises(ValueError):
        parseRanges(rangesString)

    doTest("2o15")
    doTest("2015-2011")
    doTest("2013x2014")
    doTest("2012_2013")


if __name__ == "__main__":
  main()
