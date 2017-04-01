# ranges.py

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

"""Functionality for handling sequences of Range objects."""

from deso.copyright.range import (
  Range,
)


# The character separating two ranges from each other.
RANGES_SEPARATOR = ","


def parseRanges(ranges_string):
  """Parse a range string into a sequence of Range objects."""
  # We want to be very permissive with respect to whitespaces between
  # the individual years/ranges, so strip each supposed range string
  # before trying to parse it.
  ranges_string_list = map(str.strip, ranges_string.split(RANGES_SEPARATOR))
  return list(map(Range.parse, filter(lambda x: len(x) > 0, ranges_string_list)))


def normalizeRanges(ranges):
  """Normalize a list of Range objects in-place.

    The normalization of a sequence of ranges involves two steps: First,
    the ranges are sorted such that the represented years are in
    increasing order. Second, ranges that subsume other ones are merged
    together.
  """
  # We require a sorted list of ranges to work on. Otherwise we would
  # require multiple passes of the merge loop below.
  ranges.sort()
  # We start off with the last element in the list of ranges.
  i = len(ranges) - 1

  # We loop from back to front because we remove ranges in the middle
  # and do not want our indexes to become invalid.
  while i > 0:
    range1 = ranges[i - 1]
    range2 = ranges[i]

    assert range1 <= range2, (range1, range2)

    # Check if the "smaller" range actually subsumes (contains) the
    # "larger" one. If so, merge them into a single one.
    if range2.first in range1 or range1.extendedBy(range2.first):
      del ranges[i]
      ranges[i - 1] = Range(range1.first, max(range1.last, range2.last))

      # We just removed an element. If there are no "greater" elements
      # behind us we can just decrease our index. Otherwise we need to
      # check if it is possible to merge at the same index again because
      # now we have a new element there.
      if i >= len(ranges):
        i -= 1
    else:
      i -= 1


def stringifyRanges(ranges):
  """Convert a list of ranges into a string."""
  return RANGES_SEPARATOR.join(map(str, ranges))
