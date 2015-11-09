# __init__.py

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

"""Functionality used for connecting the copyright module with git."""

from enum import (
  Enum,
)


# The section that is used for configuration of the hook in git's config.
SECTION = "copyright"
# The key representing the config option defining whether to
# automatically normalize the copyright years in files, warn if a
# header is not normalized, or error out if that is the case.
KEY_ACTION = "action"
# The key used to identify the policy to use.
KEY_POLICY = "policy"
# The key identifying the property defining whether a copyright header
# is required to exist or not.
KEY_COPYRIGHT_REQUIRED = "copyright-required"


class Action(Enum):
  """The different possible actions for copyright year normalization."""
  # Fixup any discrepancies automatically.
  Fixup = 1
  # Check if the copyright years are not properly normalized. If so,
  # error out.
  Check = 2
  # Check if the copyright years are not properly normalized. If so,
  # print a warning.
  Warn = 3

  def __str__(self):
    """Convert an Action value back into a string."""
    return str(self.name).lower()
