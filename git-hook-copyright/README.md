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
[cleanup](https://github.com/d-e-s-o/cleanup),
[execute](https://github.com/d-e-s-o/execute), and
[copyright](https://github.com/d-e-s-o/copyright) Python modules
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

The ``git`` pre-commit hook can be customized in a couple of ways to
make it more suitable for the respective workflow or environment.
Customization is achieved via the configuration infrastructure provided
by ``git`` and, hence, can be controlled on a per-repository basis or
globally (similar to the installation).


#### Policies
The hook script supports different policies that influence the behavior
during a commit of files that were found to have non-normalized
copyright headers. The pre-commit hook reads the ``copyright.policy``
configuration value. The expected value is a string that represents the
policy to use. Currently, two policies are supported: The 'plain' policy
(which is the default and used when no configuration value is set)
performs normalization and adjusts the copyright years to include the
current one.
The 'pad' policy acts similarly but in addition is able to handle
"framed" copyright headers, i.e., ones that are padded with whitespaces
(followed by other characters).

A sample invocation to set the 'pad' policy looks like this:

``$ git config copyright.policy pad``

Alternatively, one can pass the '--global' flag to the invocation to
make the change affect all repositories managed by the user. E.g.,

``$ git config --global copyright.policy pad``


#### Actions
The policy defines how to normalize a copyright header. However,
scenarios are possible where making automated changes to the the
to-be-committed files is not desired.

To that end, the hook supports "actions". Three different actions exist:
'fixup' (the default), 'check', and 'warn'. Using the 'fixup' action the
files are modified in-place. If 'check' is active then files will only
be checked for deficiencies and, if a problem is detected, an error is
raised. If the 'warn' action is in use then a message will be printed
upon a commit with a file that's copyright headers do need update but
the commit will proceed.

Actions can be configured similarly to the policy:

``$ git config --global copyright.action check``

This command would cause the hook to check if all files to commit
contain properly normalized copyright headers and error out if that is
not the case.


#### Optional Copyrights
By default, the ``git`` pre-commit hook asserts that each file that is
to be committed contains a copyright header. If that is not the case, an
error is raised and the commit fails (or some other action is taken, as
discussed above). This behavior can be altered by setting the
``copyright.copyright-required`` config option.

``$ git config --bool copyright.copyright-required false``

When set to false (the default is true), files containing no copyright
header will not be flagged.


#### Ignoring Headers
Repositories may contain files contributed by other copyright holders.
The result may be multiple copyright headers representing the various
parties. In such a scenario only one header should be adjusted when new
changes are checked-in.

The copyright hook uses a simple pattern matching approach for lines
containing the string "Copyright" to decide what lines constitute a
copyright header. However, it is possible to filter such matches against
a set of user-provided "ignore" patterns. If one of these patterns
matches, the copyright header is ignored.

These "ignore" patterns can be configured by means of the
``copyright.ignore`` config option, which may appear multiple times to
support multiple patterns as well as a mixture of local and global
configurations.

For example, a setting like:

``$ git config --add copyright.ignore 'deso@posteo\.[^ ]+'``

would cause the hook to ignore all copyright headers that contain the
string "deso@posteo." followed by a non-zero number of non-space
characters. Note that patterns have to be specified in accordance to
Python's regular expression engine.


Support
-------

The module is tested with Python 3. There is no work going on to
ensure compatibility with Python 2.
