# util.py

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

"""A module providing utility functionality."""


# A dictionary used for converting strings into booleans.
STRING_TO_BOOL_MAP = {
  "true": True,
  "false": False,
}


def stringToBool(string):
  """Convert a string into a boolean."""
  if not string in STRING_TO_BOOL_MAP:
    values = listToEnglishEnumeration(list(STRING_TO_BOOL_MAP.keys()))
    error = "\"{value}\" is not a valid boolean. Possible values are: {values}"
    error = error.format(value=string, values=values)
    raise ValueError(error)

  return STRING_TO_BOOL_MAP[string]


def listToEnglishEnumeration(l):
  """Convert a list of strings into a single string of the form 'x, y, ..., and z'."""
  assert len(l) > 0

  if len(l) == 1:
    # A single element needs no additional logic.
    return l[0]
  elif len(l) == 2:
    # A two element list would be represented as "x and y".
    return "%s and %s" % tuple(l)
  else:
    # With more than two arguments we require the form "x, y, ..., and z".
    return "%s, and %s" % (", ".join(l[:-1]), l[-1])
