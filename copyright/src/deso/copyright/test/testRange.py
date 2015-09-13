#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015 Daniel Mueller (deso@posteo.net)                   *
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

"""A test suite for the Range class."""

from deso.copyright import (
  Range,
)
from unittest import (
  main,
  TestCase,
)


class TestRange(TestCase):
  """Tests for the Range class."""
  def testCreationSucceedsForValidRange(self):
    """Verify that creation of a Range object succeeds for valid ranges."""
    Range(2015, 2015)
    Range(2014, 2015)
    Range(2013, 2015)


  def testCreationFailsIfYearsNotOrdered(self):
    """Verify that creation of a range with the first year greater than the last fails."""
    first = 2014
    last = 2013
    regex = r"%d.*is greater than.*%d" % (first, last)

    with self.assertRaisesRegex(ValueError, regex):
      Range(first, last)


  def testConversionIntoString(self):
    """Test for the conversion of a range into a string."""
    self.assertEqual(str(Range(2015, 2015)), "2015")
    self.assertEqual(str(Range(2014, 2015)), "2014-2015")
    self.assertEqual(str(Range(2013, 2015)), "2013-2015")


  def testContainmentOfYears(self):
    """Test for the "contains" functionality of a range."""
    self.assertTrue(2014 in Range(2014, 2014))
    self.assertTrue(2014 in Range(2014, 2015))
    self.assertTrue(2014 in Range(2013, 2015))


  def testExclusionOfYears(self):
    """Negative test for the "contains" functionality of a range."""
    self.assertFalse(2015 in Range(2014, 2014))
    self.assertFalse(2013 in Range(2014, 2015))
    self.assertFalse(2016 in Range(2013, 2015))


  def testExtensionCheck(self):
    """Verify that checking if a year extends a range works properly."""
    self.assertTrue(Range(2013, 2014).extendedBy(2015))


  def testNoExtension(self):
    """Negative test for the extension check functionality."""
    self.assertFalse(Range(2013, 2014).extendedBy(2016))
    self.assertFalse(Range(2013, 2014).extendedBy(2012))


  def testRangeParsing(self):
    """Verify that we can correctly parse ranges."""
    self.assertEqual(Range.parse("2014"), Range(2014, 2014))
    self.assertEqual(Range.parse("2014-2015"), Range(2014, 2015))
    self.assertEqual(Range.parse("2013-2015"), Range(2013, 2015))


  def testRangeParsingError(self):
    """Verify that we can parsing invalid range strings fails properly."""
    regex = r"Not a valid range"

    def fail(rangeString):
      """Verify that parsing of a range string fails as expected."""
      with self.assertRaisesRegex(ValueError, regex):
        Range.parse(rangeString)

    fail("x")
    fail("2013,2014-2015")
    fail("2012-2013,2015")
    fail("2012-2013x")
    fail("2012x-2013")
    fail("2012-2013-2014")


  def testRangeParsingFailsCreation(self):
    """Verify that parsing of a range fails if the years are not ordered properly."""
    regex = r"is greater than"

    with self.assertRaisesRegex(ValueError, regex):
      Range.parse("2015-2012")


  def testRangeComparison(self):
    """Verify that comparison of two ranges works properly."""
    self.assertLess(Range(2014, 2014), Range(2015, 2015))
    self.assertLess(Range(2013, 2014), Range(2014, 2015))

    self.assertEqual(Range(2013, 2013), Range(2013, 2013))
    self.assertEqual(Range(2014, 2015), Range(2014, 2015))

    self.assertNotEqual(Range(2013, 2014), Range(2013, 2015))
    self.assertNotEqual(Range(2012, 2014), Range(2013, 2014))


if __name__ == "__main__":
  main()
