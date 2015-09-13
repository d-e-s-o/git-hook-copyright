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

"""Various tests for the git pre-commit hook normalizing copyright year strings."""

from datetime import (
  datetime,
)
from deso.git.repo import (
  read,
  Repository,
  write,
)
from os import (
  chmod,
)
from os.path import (
  dirname,
  join,
)
from shutil import (
  copyfile,
  which,
)
from unittest import (
  main,
  SkipTest,
  TestCase,
)


GIT = "git"
YEAR = datetime.now().year


class GitRepository(Repository):
  """A git repository with the copyright hook installed."""
  def __init__(self):
    """Initialize the parent portion of the object."""
    super().__init__(GIT)


  def _init(self):
    """Initialize the repository and install the copyright hook."""
    super()._init()
    # We need to install our hook to get into effect for the repository
    # we just created.
    # TODO: Using a relative path based on this file might break once we
    #       install things properly, in which case the pre-commit script
    #       could reside somewhere else.
    src = join(dirname(__file__), "..", "git-hook-copyright.py")
    dst = self.path(".git", "hooks", "pre-commit")
    copyfile(src, dst)
    # The hook script is required to be executable.
    chmod(dst, 0o755)


def setUpModule():
  """Setup function invoked when loading the module."""
  if which(GIT) is None:
    raise SkipTest("%s command not found on system" % GIT)


class TestGitHook(TestCase):
  """Test for the git pre-commit hook normalizing copyright year strings."""
  def testSingleFileIsNormalized(self):
    """Verify that a single file is normalized during commit."""
    with GitRepository() as repo:
      # We already verified that replacing works correctly in
      # principle so we do not required a fully blown file here
      # potentially covering all corner-cases but can just focus on
      # the copyright header only.

      # Note that we cannot monkey patch the current year retrieval to
      # return a dummy value because git (which invokes the commit hook)
      # runs in a separate process. Instead we use the copyright year
      # 2013 as the latest year in any of the tests. Since the module
      # was authored in 2015 whatever year we currently has must be
      # greater or equal to 2015 and hence result in a separation of the
      # years via comma (because only 2014 would be merged into the
      # span).
      content = "// Copyright (c) 2013 All Right Reserved."
      expected = "// Copyright (c) 2013,%d All Right Reserved." % YEAR
      write(repo, "test.c", data=content)
      repo.add("test.c")
      repo.commit()

      new_content = read(repo, "test.c")
      self.assertEqual(new_content, expected)


  def testSingleFileWithUnstagedChangesIsNormalized(self):
    """Verify that unstaged changes are handled correctly."""
    with GitRepository() as repo:
      content1 = "// Copyright (c) 2013 All Right Reserved."
      content2 = "// Copyright (c) 2013 All Right Reserved, deso."
      expected1 = "// Copyright (c) 2013,%d All Right Reserved, deso." % YEAR
      expected2 = "// Copyright (c) 2013,%d All Right Reserved." % YEAR
      write(repo, "test.c", data=content1)
      repo.add("test.c")
      write(repo, "test.c", data=content2)
      repo.commit()

      new_content = read(repo, "test.c")
      self.assertEqual(new_content, expected1)

      # The unstaged changes must not have been commited, so if we
      # discard them we should change the content of the file once
      # more.
      repo.reset("--hard")
      new_content = read(repo, "test.c")
      self.assertEqual(new_content, expected2)


  def testBinaryFileIsIgnored(self):
    """Verify that binary files are simply ignored by the pre-commit hook."""
    with GitRepository() as repo:
      src = join(dirname(__file__), "data", "file.bin")
      dst = repo.path("file.bin")

      copyfile(src, dst)
      repo.add("file.bin")
      repo.commit()


if __name__ == "__main__":
  main()
