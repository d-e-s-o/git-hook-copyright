# range.py

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

"""Functionality for handling ranges of years."""

from collections import (
  namedtuple,
)


# The character separating two years in a range.
YEAR_SEPARATOR = "-"


class Range(namedtuple("Range", ["first", "last"])):
  """A class representing a time span between (but including) to years.

    A range is a tuple (first, last) of two years that mark a time span. Single
    years are represented as a tuple with the first year equal to the last
    year. Being a tuple, a Range is immutable.
  """
  def __new__(cls, first, last):
    """Create a new instance of Range."""
    if first > last:
      error = "First year ({first}) is greater than second year ({last})"
      error = error.format(first=first, last=last)
      raise ValueError(error)

    return tuple.__new__(cls, (first, last))


  def __str__(self):
    """Convert a range into a string."""
    if self.first == self.last:
      return "%d" % self.first
    else:
      return "%d%s%d" % (self.first, YEAR_SEPARATOR, self.last)


  def __contains__(self, year):
    """Check whether a year is contained in a range."""
    return self.first <= year and year <= self.last


  def __compare__(self, range_):
    """Compare two ranges."""
    return self.first - range_.first or self.last - range_.last


  def extendedBy(self, year):
    """Check whether a year extends a given range.

      Note that for simplicity only upper extension is considered, that is, a
      year smaller than the given range is never considered to extend it. By
      only working on a sorted list of years this property can be satisfied
      trivially.
    """
    return year == self.last + 1


  @staticmethod
  def parse(string):
    """Parse a range from a string."""
    try:
      # A range of years can be represented in two ways. If it is a single
      # year, we can convert it into an integer directly.
      year = int(string)
      return Range(year, year)
    except ValueError:
      # If this cast did not work we must have gotten a "true" range, e.g.,
      # 2010-2012.
      try:
         # We might not have enough elements in the list, too many, or we might
         # again fail to convert them to integers. In any case a ValueError is
         # raised.
        first, last = list(map(int, string.split(YEAR_SEPARATOR)))
      except ValueError:
        raise ValueError("Not a valid range: \"%s\"" % string)

      return Range(first, last)
