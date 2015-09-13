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
  normalizeContent,
)
from os.path import (
  basename,
)
from subprocess import (
  check_call,
  check_output,
)
from tempfile import (
  NamedTemporaryFile,
)


# The command for invoking git.
GIT = "git"


def changedFiles():
  """Retrieve a list of changed files."""
  # We only care for Added (A) and Modified (M) files.
  cmd = [GIT, "diff", "--staged", "--name-only", "--diff-filter=AM", "--no-color", "--no-prefix"]
  out = check_output(cmd)
  return out.decode("utf-8").splitlines()


def stagedFileContent(path):
  """Retrieve the file content of a file in a git repository including any staged changes."""
  return check_output([GIT, "cat-file", "--textconv", ":%s" % path]).decode("utf-8")


def stageFile(path):
  """Stage a file in git."""
  check_call([GIT, "add", path])


def normalizeStagedFile(path):
  """Normalize a file in a git repository staged for commit."""
  # The procedure for normalizing an already staged file is not as
  # trivial as it might seem at first glance. Things get complicated
  # when considering that only parts of the changes to a file might be
  # staged for commit and others were not yet considered (yet, they
  # exist in the file on disk).
  # The approach we take is to first create a temporary copy of the full
  # file. Next, we ask git for the content of the file without the
  # unstaged changes, normalize it, and write it into the original file.
  # Afterwards we staged this file's new contents. Last we take the
  # original content (including any unstaged changes), normalize it as
  # well, and write that into the original file.

  # We use a temporary file for backing up the original content of the
  # file we work on in the git repository. We could keep the content
  # in memory only, but as a safety measure (in case Python crashes in
  # which case proper exception handling does not help) it might be
  # worthwhile to have it on disk (well, in a file; it could just reside
  # in a ramdisk, but that really is out of our control and not that
  # important).
  # Note that we open all files in text mode (as opposed to binary
  # mode). That is because we only want to work on text files. If a
  # binary file is committed we will get some sort of decoding error and
  # bail out.
  with NamedTemporaryFile(mode="w", prefix=basename(path)) as file_tmp:
    staged_content = stagedFileContent(path)
    normalized_content = normalizeContent(staged_content)

    # In many cases we expect the normalization to cause no change to
    # the content. We essentially special-case for that expectation and
    # only cause additional I/O if something truly changed.
    if normalized_content != staged_content:
      # We need to copy the file of interest from the git repository
      # into some other location.
      with open(path, "r+") as file_git:
        original_content = file_git.read()
        file_tmp.write(original_content)
        file_git.seek(0)
        file_git.write(normalized_content)
        file_git.truncate()

      # Stage the normalized file. It is now in the state we want it to
      # be committed.
      stageFile(file_git.name)

      with open(path, "w") as file_git:
        # Last we need to write back the original content. However, we
        # normalize it as well.
        file_git.write(normalizeContent(original_content))
        file_git.truncate()


def main():
  """Find all files to commit and normalize them before the commit takes place."""
  for file_git_path in changedFiles():
    normalizeStagedFile(file_git_path)


if __name__ == "__main__":
  main()
