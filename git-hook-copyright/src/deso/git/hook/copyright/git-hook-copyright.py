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

"""A pre-commit hook normalizing the copyright year strings of all to-be-committed files."""

from deso.copyright import (
  normalizeFiles,
)
from subprocess import (
  check_call,
  check_output,
)


# The command for invoking git.
GIT = "git"


def changedFiles():
  """Retrieve a list of changed files."""
  # We only care for Added (A) and Modified (M) files.
  cmd = [GIT, "diff", "--staged", "--name-only", "--diff-filter=AM", "--no-color", "--no-prefix"]
  out = check_output(cmd)
  return out.decode("utf-8").splitlines()


def stageFile(path):
  """Stage a file in git."""
  check_call([GIT, "add", path])


def main():
  """Find all files to commit and normalize them before the commit takes place."""
  for file_git_path in changedFiles():
    normalizeFiles([file_git_path])
    # TODO: We stage the entire file here. It might include previously
    #       unstaged changes.
    stageFile(file_git_path)


if __name__ == "__main__":
  main()
