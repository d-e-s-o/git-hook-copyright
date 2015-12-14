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

"""Extend the copyright years of all committed files with the commit year."""

from copyright import (
  normalizeContentPadded,
  normalizeFiles,
)
from datetime import (
  date,
)
from subprocess import (
  check_output,
)


# The command for invoking git.
GIT = "git"


def changedFiles():
  """Retrieve a list of affected files."""
  cmd = [GIT, "log", "--relative", "--name-only", "--max-count=1", "--format=format:", "HEAD"]
  out = check_output(cmd)
  return out.decode("utf-8").splitlines()


def commitYear():
  """Retrieve the year of the current (i.e., HEAD) commit."""
  cmd = [GIT, "log", "--date=default", "--max-count=1", "--format=format:%at", "HEAD"]
  out = check_output(cmd)
  # We retrieved a UNIX timestamp, i.e., the seconds from 1.1.1970. All
  # we have to do is to treat that value as an integer and create a date
  # object from it.
  return date.fromtimestamp(int(out)).year


def main():
  """Retrieve the changed files and the commit year and adjust the copyright headers."""
  files = changedFiles()
  year = commitYear()
  normalizeFiles(files, normalizeContentPadded, year)


if __name__ == "__main__":
  main()
