git-hook-copyright
==================


Purpose
-------

**git-hook-copyright** is a pre-commit hook script to be used in
conjunction with ``git`` (see githooks(5) for more general information
on hooks). A pre-commit hook is executed just before a commit takes
place. It allows for things such as sanity checking of the
to-be-committed files.

The **git-hook-copyright** in particular works on the copyright years
often found in source code files. It can be used to normalize them (that
is, merge redundant years in order to provide the shortest
semantic-preserving string possible), check for validity and
up-to-dateness, or to assert that a file contains a copyright header in
the first place. The hook is particularly useful in conjunction with
large code bases and when touching a lot of files (with each
modification ideally causing an update of the copyright years, if
required). In such scenarios, a manual of the copyright headers is a
tedious and easy forgettable task.


Installation
------------

In order to use **git-hook-copyright** the
[copyright](https://github.com/d-e-s-o/copyright) Python module
(contained in the repository in compatible and tested versions) need to
be accessible by Python (typically by installing them in a directory
listed in ``PYTHONPATH`` or adjusting the latter to point to each of
them).

Installation of the hook requires two steps. First, the module's source
code needs to be discoverable in Python's search path. On [Gentoo
Linux](https://www.gentoo.org/), the provided
[ebuild](https://github.com/d-e-s-o/git-hook-copyright-ebuild) can be
used to install the module on the system. On other systems the
``PYTHONPATH`` environment variable could be adjusted within some
initialization file to include the path the module resides at or the
module could be copied into one of the folders searched by default.

Second, the ``git`` commit hook needs to be installed. Installation can
either happen on a local, i.e., per-repository, basis or globally. A
local installation is as simple as creating a symbolic link of the file
``git-hook-copyright/src/git/hook/copyright/copyright_.py`` to
``<repository>/.git/hooks/pre-commit``.

For a global installation (only affecting newly created or
re-initialized repositories by the current user) one needs to associate
the ``pre-commit`` hook file with the default template that ``git`` uses
for laying out repository meta-data. E.g.,

``$ git config --global init.templatedir ~/.git-templates``

would instruct ``git`` to use ``~/.git-templates`` as the directory in
which to search for templates to apply upon repository creation. Next,
one has to create a ``hooks`` sub-directory (``~/.git-templates/hooks/``)
and copy or link the file ``src/copyright/git/pre-commit`` into it. Care
must be taken that the resulting or referenced (in case of a symbolic
link) file is executable.

If the hook should be installed for existing repositories, those would
require re-initialization. Some shell trickery can help out here, for
instance:

``$ find <dir> -iname ".git" -type d | sed 's!.*!(rm \0/hooks/pre-commit; cd \0/..; git init)!g' | sh``

will find all repositories below ``<dir>`` and re-initialize them. Note
that it removes any previously installed pre-commit hook. ``git init``
would not overwrite such files.


Configuration
-------------

The ``git`` pre-commit hook supports different policies. The policy to
use is defined using the configuration infrastructure provided by
``git``. Hence, configuration can happen on a per-repository basis or
globally (similar to the installation).

The pre-commit hook reads the ``copyright.policy`` configuration value.
The expected value is a string that represents the policy to use.
Currently, only the 'plain' policy is supported, which is also enabled
by default.

A sample invocation to set the 'plain' policy looks like this:

``$ git config copyright.policy plain``

Alternatively, one can pass the '--global' flag to the invocation to
make the change affect all repositories managed by the user. E.g.,

``$ git config --global copyright.policy plain``


Support
-------

The module is tested with Python 3. There is no work going on to
ensure compatibility with Python 2.
