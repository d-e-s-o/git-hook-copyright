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

from datetime import (
  datetime,
)
from deso.copyright import (
  normalizeContent,
  policyStringToFunction,
)
from deso.copyright.util import (
  listToEnglishEnumeration,
  stringToBool,
)
from deso.git.hook.copyright import (
  Action,
  KEY_ACTION,
  KEY_COPYRIGHT_REQUIRED,
  KEY_POLICY,
  SECTION,
)
from os.path import (
  basename,
)
from subprocess import (
  CalledProcessError,
  check_call,
  check_output,
)
from sys import (
  exit as exit_,
  stderr,
)
from tempfile import (
  NamedTemporaryFile,
)
from traceback import (
  print_exc,
)


# The command for invoking git.
GIT = "git"


# A dictionary for converting action strings into the proper action
# types.
STRING_TO_ACTION_MAP = {
  str(Action.Fixup): Action.Fixup,
  str(Action.Check): Action.Check,
  str(Action.Warn): Action.Warn,
}


def stringToAction(string):
  """Convert a string into an action type."""
  if not string in STRING_TO_ACTION_MAP:
    values = listToEnglishEnumeration(list(STRING_TO_ACTION_MAP.keys()))
    error = "\"{value}\" is not a valid action. Possible values are: {values}"
    error = error.format(value=string, values=values)
    raise ValueError(error)

  return STRING_TO_ACTION_MAP[string]


def changedFiles():
  """Retrieve a list of changed files."""
  # We only care for Added (A) and Modified (M) files.
  cmd = [GIT, "diff", "--staged", "--name-only", "--diff-filter=AM", "--no-color", "--no-prefix"]
  out = check_output(cmd)
  return out.decode("utf-8").splitlines()


def retrieveConfigValue(key, *args):
  """Retrieve a git configuration value associated with a key."""
  try:
    name = "%s.%s" % (SECTION, key)
    out = check_output([GIT, "config", "--null"] + list(args) + [name])
    # The output is guaranteed to be terminated by a NUL byte. We want
    # to discard that.
    return out[:-1].decode("utf-8")
  except CalledProcessError:
    # In case the configuration value is not set we just return None.
    return None


def retrieveActionType():
  """Retrieve the to perform with respect to copyright year normalization."""
  string = retrieveConfigValue(KEY_ACTION)
  if string is None:
    # By default we write out any discrepancies.
    return Action.Fixup

  return stringToAction(string)


def retrieveNormalizationFunction():
  """Retrieve the normalization policy set for the repository."""
  policy = retrieveConfigValue(KEY_POLICY)
  if policy is None:
    return normalizeContent

  return policyStringToFunction(policy, RuntimeError)


def copyrightHeaderMustExist():
  """Check whether a copyright header must exist."""
  required = retrieveConfigValue(KEY_COPYRIGHT_REQUIRED, "--bool")
  if required is None:
    # By default we require a copyright header.
    return True

  return stringToBool(required)


def stagedFileContent(path):
  """Retrieve the file content of a file in a git repository including any staged changes."""
  return check_output([GIT, "cat-file", "--textconv", ":%s" % path]).decode("utf-8")


def stagedChangesRevertFileContent(path):
  """Check whether the staged changes revert the changes of the HEAD commit for the given file."""
  try:
    # By using the --exit-code option git will return 1 in case the diff
    # is not empty and 0 if it is.
    check_call([GIT, "diff", "--staged", "--quiet", "--exit-code", "HEAD^", path])
    # If the git invocation succeeded the diff was empty and the
    # currently staged changes for the given file revert the ones made
    # in the HEAD commit.
    return True
  except CalledProcessError:
    # The diff was not empty or the command failed for some other
    # reason (e.g., because there is no HEAD^ commit). In any case, we
    # should go ahead with the commit.
    return False


def stageFile(path):
  """Stage a file in git."""
  check_call([GIT, "add", path])


def normalizeStagedFile(path, normalize_fn, year, action):
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
    normalized_content, found = normalize_fn(staged_content, year=year)

    # In many cases we expect the normalization to cause no change to
    # the content. We essentially special-case for that expectation and
    # only cause additional I/O if something truly changed.
    if found > 0 and normalized_content != staged_content:
      if action == Action.Check or action == Action.Warn:
        print("Copyright years in %s are not properly normalized" % path,
              file=stderr)
        if action == Action.Check:
          exit_(1)

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
        content, _ = normalize_fn(original_content, year=year)
        file_git.write(content)
        file_git.truncate()

    return found


def main():
  """Find all files to commit and normalize them before the commit takes place."""
  action = retrieveActionType()
  normalize_fn = retrieveNormalizationFunction()
  required = copyrightHeaderMustExist()
  # We always want to extend the copyright year range with the current
  # year.
  year = datetime.now().year

  for file_git_path in changedFiles():
    # When amending commits it is possible that all changes to a file
    # are reverted. In this case we want to omit this file from
    # normalization because we effectively made no changes to the file
    # and, hence, we should not touch the copyright header either.
    # Unfortunately, we have no way of knowing whether we are dealing
    # with an amendment or a new commit.
    if stagedChangesRevertFileContent(file_git_path):
      continue

    try:
      found = normalizeStagedFile(file_git_path, normalize_fn, year, action)
      # If a copyright header is required but we did not find one we
      # signal that to the user and abort.
      if required and found <= 0:
        print("Error: No copyright header found in %s" % file_git_path,
              file=stderr)
        exit_(1)
    except UnicodeDecodeError:
      # We may get a decode error in case of a binary file that we
      # simply cannot handle properly. We want to ignore those files
      # silently.
      pass
    except Exception as e:
      print("The copyright pre-commit hook encountered an error while "
            "processing file %s: \"%s\"" % (file_git_path, e), file=stderr)
      print_exc(file=stderr)
      exit_(1)


if __name__ == "__main__":
  main()
