# normalize.py

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

"""A script able to detect and normalize copyright year strings."""

from argparse import (
  ArgumentParser,
  ArgumentTypeError,
)
from datetime import (
  datetime,
)
from deso.copyright.range import (
  Range,
  YEAR_SEPARATOR,
)
from deso.copyright.ranges import (
  normalizeRanges,
  parseRanges,
  RANGES_SEPARATOR,
  stringifyRanges,
)
from deso.copyright.util import (
  listToEnglishEnumeration,
)
from re import (
  compile as regex,
  escape,
  IGNORECASE,
)
from sys import (
  argv as sysargv,
)


ANY_R = r"[^\n\r]"
# A regular expression string representing a single year. Note that we
# deliberately do not require a year to start with a number not equal to
# zero. Sometimes years are shortened, e.g., 98 could represent 1998 or
# 07 could stand for 2007, and we want to match those years as well. We
# might fail because of that, but at least we raise awareness (for a
# "wrong" [in this program's sense] year representation).
YEAR_R = r"[0-9]+"
YEAR_SEP_R = escape(YEAR_SEPARATOR)
RANGES_SEP_R = escape(RANGES_SEPARATOR)
# A regular expression string representing copyright years.
CYEARS = r"{y}(?:\s*[{s1}{s2}]\s*{y})*"
CYEARS_R = CYEARS.format(y=YEAR_R, s1=YEAR_SEP_R, s2=RANGES_SEP_R)
PREFIX = r"copyright(?:{a}(?!{c}))*{a}"
PREFIX_R = PREFIX.format(a=ANY_R, c=CYEARS_R)
# A regular expression string representing what we expect a line with a
# copyright reference to look like. Note that the regular expression can
# not only work on a line-by-line but also a per-file basis. In fact,
# that is the intended usage because then we do not have to care about
# different line endings when writing out data.
COPYRIGHT = r"({p})({c})"
COPYRIGHT_R = COPYRIGHT.format(p=PREFIX_R, c=CYEARS_R)
# The final regular expression able to capture a copyright line.
COPYRIGHT_RE = regex(COPYRIGHT_R, IGNORECASE)


def normalizeContent(content):
  """Normalize the copyright headers in a string representing a file."""
  # For our year extension we need the current year.
  current_year = datetime.now().year
  # Because we work with ranges we need a range representing the current
  # year.
  current_year_range = Range(current_year, current_year)

  def normalizeCopyrightYears(match):
    """Parse the copyright year string and normalize it."""
    prefix, range_string = match.groups()
    ranges = parseRanges(range_string)
    # Not only do we want to normalize the existing copyright year
    # string, we potentially want to extend it with the current year if
    # that is not already included.
    ranges.append(current_year_range)
    normalizeRanges(ranges)

    return prefix + stringifyRanges(ranges)

  return COPYRIGHT_RE.sub(normalizeCopyrightYears, content)


def normalizeFiles(files, normalize_fn=normalizeContent):
  """Normalize the copyright headers of a list of files."""
  for file_ in files:
    with open(file_, "r+") as f:
      content = f.read()
      new_content = normalize_fn(content)
      if new_content != content:
        f.seek(0)
        f.write(new_content)
        # Remove potentially remaining data. We might just have merged
        # some years together so the new content might be smaller than
        # the previous one.
        f.truncate()


# A mapping from policy strings to content normalization functions.
POLICY_MAP = {
  "plain": normalizeContent,
}


def policyStringToFunction(policy, ErrorType=ArgumentTypeError):
  """Map a policy string to a normalization function using this policy."""
  if not policy in POLICY_MAP:
    policies = listToEnglishEnumeration(list(POLICY_MAP.keys()))
    error = "Unsupported policy: \"{policy}\". Supported policies are: {policies}"
    error = error.format(policy=policy, policies=policies)
    raise ErrorType(error)

  return POLICY_MAP[policy]


def setupArgumentParser():
  """Create and initialize an argument parser, ready for use."""
  parser = ArgumentParser()
  parser.add_argument(
    "files", action="store", metavar="files", nargs="+",
    help="A list of files to check and potentially fix up the copyright "
         "headers for the current year.",
  )
  parser.add_argument(
    "--policy", action="store", default=normalizeContent,
    dest="normalization_fn", metavar="policy",
    type=policyStringToFunction,
    help="Specify a policy to use. A policy influences the way "
         "normalization is performed. Available options are: %s." %
         listToEnglishEnumeration(list(POLICY_MAP.keys())),
  )
  return parser


def main(argv):
  """The main function parses the script's arguments and acts upon them."""
  parser = setupArgumentParser()
  ns = parser.parse_args(argv[1:])

  normalizeFiles(ns.files, normalize_fn=ns.normalization_fn)
  return 0


if __name__ == "__main__":
  exit(main(sysargv))
