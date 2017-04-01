# normalize.py

#/***************************************************************************
# *   Copyright (C) 2015-2017 Daniel Mueller (deso@posteo.net)              *
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
  search,
)
from sys import (
  argv as sysargv,
)


ANY_R = r"[^\n\r]"
TWO_SPACES_RE = regex(r"  ")
# A regular expression string representing a single year. Note that we
# deliberately do not require a year to start with a number not equal to
# zero. Sometimes years are shortened, e.g., 98 could represent 1998 or
# 07 could stand for 2007, and we want to match those years as well. We
# might fail because of that, but at least we raise awareness (for a
# "wrong" [in this program's sense] year representation).
YEAR_R = r"[0-9]+"
YEAR_SEP_R = escape(YEAR_SEPARATOR)
RANGES_SEP_R = escape(RANGES_SEPARATOR)
# A regular expression string representing copyright years. Note that we
# consume any trailing range separators here silently.
CYEARS = r"{y}(?:\s*[{s1}{s2}]\s*{y})*{s2}*"
CYEARS_R = CYEARS.format(y=YEAR_R, s1=YEAR_SEP_R, s2=RANGES_SEP_R)
PREFIX = r"copyright(?:{a}(?!{c}))*{a}"
PREFIX_R = PREFIX.format(a=ANY_R, c=CYEARS_R)
SUFFIX = r"{a}*"
SUFFIX_R = SUFFIX.format(a=ANY_R)
# A regular expression string representing what we expect a line with a
# copyright reference to look like. Note that the regular expression can
# not only work on a line-by-line but also a per-file basis. In fact,
# that is the intended usage because then we do not have to care about
# different line endings when writing out data.
COPYRIGHT = r"({p})({c})({s})"
COPYRIGHT_R = COPYRIGHT.format(p=PREFIX_R, c=CYEARS_R, s=SUFFIX_R)
# The final regular expression able to capture a copyright line.
COPYRIGHT_RE = regex(COPYRIGHT_R, IGNORECASE)


def _matchesIgnoreList(string, ignore=None):
  """Check if a string is matched by an element in the ignore list."""
  if ignore is None:
    return False

  for item in ignore:
    m = search(item, string)
    if m is not None:
      return True

  return False


def _normalizeContent(content, normalize_fn, ignore=None):
  """Normalize the copyright headers in a string using the given function."""
  pos = 0
  found = 0

  while True:
    match = COPYRIGHT_RE.search(content, pos=pos)
    if match is None:
      # We have scanned the entire content and there are no more
      # matches.
      return content, found

    start = match.start()
    end = match.end()
    pos = end
    string = match.string[start:end]
    if _matchesIgnoreList(string, ignore):
      # The string is on the ignore list. Just continue with the next
      # occurrence.
      continue

    replacement, matched = COPYRIGHT_RE.subn(normalize_fn, string, count=1)
    assert matched == 1

    content = content[:start] + replacement + content[end:]
    found += matched


def normalizeContent(content, year=None, ignore=None):
  """Normalize the copyright headers in a string representing a file."""
  def normalizeCopyrightYears(match):
    """Parse the copyright year string and normalize it."""
    prefix, range_string, suffix = match.groups()
    ranges = parseRanges(range_string)
    # Not only do we want to normalize the existing copyright year
    # string, we potentially want to extend it with a given year if that
    # is not already included.
    if year is not None:
      ranges.append(Range(year, year))

    normalizeRanges(ranges)

    return prefix + stringifyRanges(ranges) + suffix

  return _normalizeContent(content, normalizeCopyrightYears,
                           ignore=ignore)


def normalizeContentPadded(content, year=None, ignore=None):
  """Normalize the copyright headers in a string representing a file.

    This function normalizes the copyright headers in a string. It also
    tries to fix any whitespace paddings, for instance, in case the text
    is framed at a fixed width.
  """
  def removeSpace(_):
    """Replace a two space match with a single space."""
    return " "

  def normalizeCopyrightYearsPadded(match):
    """Parse the copyright year string and normalize it."""
    prefix, range_string, suffix = match.groups()

    ranges = parseRanges(range_string)
    if year is not None:
      ranges.append(Range(year, year))

    normalizeRanges(ranges)

    new_range_string = stringifyRanges(ranges)
    increase = len(new_range_string) - len(range_string)

    if increase > 0:
      # If the copyright year string got longer we remove that many
      # spaces from the following suffix (if possible).
      new_suffix = TWO_SPACES_RE.sub(removeSpace, suffix, count=increase)
    elif increase < 0:
      # If the copyright year string got actually smaller (because we
      # were able to merge years), we insert as many spaces into the
      # suffix as we removed characters.
      spaces = "  " + " " * -increase
      new_suffix = TWO_SPACES_RE.sub(spaces, suffix, count=1)
    else:
      new_suffix = suffix

    return prefix + new_range_string + new_suffix

  return _normalizeContent(content, normalizeCopyrightYearsPadded,
                           ignore=ignore)


def normalizeFiles(files, normalize_fn=normalizeContent, year=None, ignore=None):
  """Normalize the copyright headers of a list of files."""
  for file_ in files:
    with open(file_, "r+") as f:
      content = f.read()
      new_content, found = normalize_fn(content, year=year, ignore=ignore)
      if found > 0 and new_content != content:
        f.seek(0)
        f.write(new_content)
        # Remove potentially remaining data. We might just have merged
        # some years together so the new content might be smaller than
        # the previous one.
        f.truncate()


# A mapping from policy strings to content normalization functions.
POLICY_MAP = {
  "plain": normalizeContent,
  "pad": normalizeContentPadded,
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
  parser.add_argument(
    "--year", action="store", default=None, metavar="year", type=int,
    help="Specify a year to extend the copyright year range by. By "
         "default the copyright years are just normalizaed, not "
         "extended.",
  )
  parser.add_argument(
    "--ignore", action="append", default=[], metavar="ignore",
    help="Ignore copyright headers matching a certain pattern. That is, "
         "if a copyright " "replacement is about to be made it will be "
         "cancelled if the very match also matches the pattern provided "
         "via this argment. This option can be supplied multiple times.",
  )
  return parser


def main(argv):
  """The main function parses the script's arguments and acts upon them."""
  parser = setupArgumentParser()
  ns = parser.parse_args(argv[1:])

  normalizeFiles(ns.files, normalize_fn=ns.normalization_fn,
                 year=ns.year, ignore=ns.ignore)
  return 0


if __name__ == "__main__":
  exit(main(sysargv))
