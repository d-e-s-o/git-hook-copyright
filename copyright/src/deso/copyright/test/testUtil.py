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

"""Tests for the utility functionality."""

from deso.copyright.util import (
  listToEnglishEnumeration,
)
from unittest import (
  main,
  TestCase,
)


class TestUtil(TestCase):
  """Tests for the utility functionality."""
  def testEnglishEnumerationStringCreation(self):
    """Test for listToEnglishEnumeration with various enumerations."""
    def doTest(list_, expected):
      """Given a list of values, verify that the created string is as expected."""
      value = listToEnglishEnumeration(list_)
      self.assertEqual(value, expected)

    doTest(["only-item"], "only-item")
    doTest(["first", "second"], "first and second")
    doTest(["a", "b", "c"], "a, b, and c")
    doTest(["4", "3", "2", "0"], "4, 3, 2, and 0")


if __name__ == "__main__":
  main()
