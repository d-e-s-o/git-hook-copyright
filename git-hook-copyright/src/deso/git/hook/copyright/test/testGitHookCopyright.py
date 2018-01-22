#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015,2017-2018 Daniel Mueller (deso@posteo.net)         *
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
from deso.execute import (
  findCommand,
  ProcessError,
)
from deso.git.hook.copyright import (
  Action,
  KEY_ACTION,
  KEY_COPYRIGHT_REQUIRED,
  KEY_IGNORE,
  KEY_POLICY,
  SECTION,
)
from deso.git.repo import (
  PathMixin,
  PythonMixin,
  read,
  Repository,
  write,
)
from os import (
  chmod,
  symlink,
)
from os.path import (
  dirname,
  join,
)
from shutil import (
  copyfile,
)
from unittest import (
  main,
  TestCase,
)


GIT = findCommand("git")
YEAR = datetime.now().year


class GitRepository(PathMixin, PythonMixin, Repository):
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


class TestGitHook(TestCase):
  """Test for the git pre-commit hook normalizing copyright year strings."""
  def testInvalidPolicyIsComplainedAbout(self):
    """Verify that if an invalid/unsupported policy is set, we get an error."""
    with GitRepository() as repo:
      repo.config(SECTION, KEY_POLICY, "invalid")
      write(repo, "foo.cpp", data="")
      repo.add("foo.cpp")

      with self.assertRaises(ProcessError):
        repo.commit()


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


  def testSingleFileWithPadPolicy(self):
    """Verify that the commit hook can use the 'pad' policy."""
    with GitRepository() as repo:
      content = "* Copyright (C) 2010,2011,2012,2013 Daniel Mueller (deso@posteo.net)  *"
      expected = "* Copyright (C) 2010-2013,%d Daniel Mueller (deso@posteo.net)       *" % YEAR
      repo.config(SECTION, KEY_POLICY, "pad")
      write(repo, "test.py", data=content)
      repo.add("test.py")
      repo.commit()

      new_content = read(repo, "test.py")
      self.assertEqual(new_content, expected)


  def testBinaryFileIsIgnored(self):
    """Verify that binary files are simply ignored by the pre-commit hook."""
    with GitRepository() as repo:
      src = join(dirname(__file__), "data", "file.bin")
      dst = repo.path("file.bin")

      copyfile(src, dst)
      repo.add("file.bin")
      repo.commit()


  def testCopyrightHeaderRequired(self):
    """Test that the copyright.copyright-required setting is handled correctly."""
    def doTest(content, fail, required=None):
      """Perform a single commit test and check for success or failure."""
      with GitRepository() as repo:
        if required is not None:
          repo.config(SECTION, KEY_COPYRIGHT_REQUIRED, str(required))

        write(repo, "test.c", data=content)
        repo.add("test.c")

        if fail:
          regex = r"No copyright header found"
          with self.assertRaisesRegex(ProcessError, regex):
            repo.commit()
        else:
          repo.commit()

    # If no copyright header is given a commit must fail unless we
    # explicitly set copyright-required to false.
    doTest("int main() { return 0; }", True)
    doTest("int main() { return 0; }", True, required=True)
    doTest("int main() { return 0; }", False, required=False)
    # If a copyright header is given a commit must succeed in all cases.
    doTest("/* Copyright (C) 2015 Daniel Mueller (deso@posteo.net) */", False)
    doTest("/* Copyright (C) 2015 Daniel Mueller (deso@posteo.net) */", False, required=True)
    doTest("/* Copyright (C) 2015 Daniel Mueller (deso@posteo.net) */", False, required=False)


  def testCopyrightAction(self):
    """Verify that the various actions are handled correctly."""
    def doTest(action=None):
      """Test the pre-commit hook for the given action."""
      content = "// Copyright (C) 1999, 2013"
      expected = "// Copyright (C) 1999,2013,%d" % YEAR

      with GitRepository() as repo:
        if action is not None:
          repo.config(SECTION, KEY_ACTION, str(action))

        write(repo, "test.cpp", data=content)
        repo.add("test.cpp")

        regex = r"are not properly normalized"
        # By default (no action set), we implicitly use the fixup
        # action and correct any issues with the copyright header
        # directly.
        if action is None or action == Action.Fixup:
          repo.commit()
          self.assertEqual(read(repo, "test.cpp"), expected)
        elif action == Action.Check:
          with self.assertRaisesRegex(ProcessError, regex):
            repo.commit()
        elif action == Action.Warn:
          _, err = repo.commit()
          self.assertIn(b"are not properly normalized", err)
        else:
          assert False, action

    doTest()
    doTest(Action.Fixup)
    doTest(Action.Check)
    doTest(Action.Warn)


  def testChangeReversion(self):
    """Verify that file change reversals are detected and files exluded from normalization."""
    with GitRepository() as repo:
      file_ = "some-file.txt"
      content1 = "# Copyright (c) 2013 All Right Reserved.\n"
      content2 = "# This is a comment!"
      expected1 = "# Copyright (c) 2013,%d All Right Reserved.\n" % YEAR

      write(repo, file_, data=content1)
      repo.add(file_)
      # We want to commit the unmodified content (i.e., without
      # copyright header normalization).
      repo.commit("--no-verify")

      write(repo, file_, data=content2, truncate=False)
      repo.add(file_)
      repo.commit()

      self.assertEqual(read(repo, file_), expected1 + content2)

      # Now we write back the previous content. Once we commit the
      # change the commit hook should detect that we effectively
      # reverted the file content and not apply any normalization.
      write(repo, file_, data=content1)
      repo.add(file_)
      # Add another file to the repository in order to not let the
      # commit become empty (that would not be a problem but it is very
      # unusual and not the case we want to test here).
      write(repo, "test.dat", data="# Copyright (c) %d." % YEAR)
      repo.add("test.dat")
      repo.commit("--amend")

      # The file must contain the original copyright header and not have
      # been normalized afterwards.
      self.assertEqual(read(repo, file_), content1)


  def testIgnore(self):
    """Verify that copyright.ignore setting is handled correctly."""
    with GitRepository() as repo:
      content = """\
        * Copyright (C) 2010,2011,2012,2013 foo                *
        * Copyright (C) 2013,2014 bar                          *
        * Copyright (C) 2013,2014 baz                          *
        * Copyright (C) 2010 Daniel Mueller (deso@posteo.net)  *
      """
      expected = """\
        * Copyright (C) 2010,2011,2012,2013 foo                *
        * Copyright (C) 2013,2014 bar                          *
        * Copyright (C) 2013-2014,%d baz                     *
        * Copyright (C) 2010 Daniel Mueller (deso@posteo.net)  *
      """ % YEAR
      repo.config(SECTION, KEY_IGNORE, r"foo", "--add")
      repo.config(SECTION, KEY_IGNORE, r"bar", "--add")
      repo.config(SECTION, KEY_IGNORE, r"deso@posteo\.[^ ]+", "--add")
      repo.config(SECTION, KEY_POLICY, r"pad")

      write(repo, "copyright.py", data=content)
      repo.add("copyright.py")
      repo.commit()

      new_content = read(repo, "copyright.py")
      self.assertEqual(new_content, expected)


  def testSubmoduleHandling(self):
    """Verify that submodules are handled correctly."""
    with GitRepository() as lib,\
         GitRepository() as app:
      content = "// Copyright (c) 2013 All Right Reserved."
      expected = "// Copyright (c) 2013,%d All Right Reserved." % YEAR

      write(lib, "lib.dat", data=content)
      lib.add("lib.dat")
      lib.commit()

      app.submodule("add", lib.path())
      app.commit()

      self.assertEqual(read(lib, "lib.dat"), expected)


  def testSymlinks(self):
    """Verify that symbolic links are handled correctly."""
    with GitRepository() as repo:
      repo.config(SECTION, KEY_COPYRIGHT_REQUIRED, str(True))

      write(repo, "repo.dat", data="foobar")
      symlink(repo.path("repo.dat"), repo.path("repo.lnk"))

      repo.add("repo.lnk")
      repo.commit()


if __name__ == "__main__":
  main()
