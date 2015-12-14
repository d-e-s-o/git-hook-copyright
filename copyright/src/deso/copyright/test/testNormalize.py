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

"""Test suite for the copyright year string normalization script."""

from deso.copyright.normalize import (
  main as normalizeMain,
)
from sys import (
  argv as sysargv,
)
from tempfile import (
  NamedTemporaryFile,
)
from unittest import (
  main,
  TestCase,
)


COPYRIGHT_MSFT_TEMPLATE = """\
// <copyright file="test.cs" company="MSFT">
%s
//
// This source is subject to the Microsoft Permissive License.
// Please see the License.txt file for more information.
// All other rights reserved.
//
// THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
// KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
// PARTICULAR PURPOSE.
"""
COPYRIGHT_MSFT_LINE = """\
// Copyright (c) 2007, 2008 All Right Reserved, http://microsoft.com/\
"""
COPYRIGHT_MSFT_LINE_FIXED = """\
// Copyright (c) 2007-2008,2015 All Right Reserved, http://microsoft.com/\
"""

COPYRIGHT_VMW_TEMPLATE = """\
/*********************************************************
%s
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation version 2.1 and no later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the Lesser GNU General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA.
 *
 *********************************************************/\
"""
COPYRIGHT_VMW_LINE = """\
 * Copyright (C) 1999,2000,2012-2014 VMware, Inc. All rights reserved.\
"""
COPYRIGHT_VMW_LINE_FIXED = """\
 * Copyright (C) 1999-2000,2012-2015 VMware, Inc. All rights reserved.\
"""

COPYRIGHT_GENTOO_TEMPLATE = """\
%s
# Distributed under the terms of the GNU General Public License v2\
"""
COPYRIGHT_GENTOO_LINE = """\
# Copyright 2013,2012,1995-2014 Gentoo Foundation\
"""
COPYRIGHT_GENTOO_LINE_FIXED = """\
# Copyright 1995-2015 Gentoo Foundation\
"""
COPYRIGHT_GENTOO_LINE_FIXED_NO_2015 = """\
# Copyright 1995-2014 Gentoo Foundation\
"""

COPYRIGHT_DESO_TEMPLATE = """\
#/***************************************************************************
%s
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
# ***************************************************************************/\
"""
COPYRIGHT_DESO_LINE1 = """\
# * Copyright (C) 2012,2013,2014,2015 Daniel Mueller (deso@posteo.net)      *\
"""
COPYRIGHT_DESO_LINE1_FIXED = """\
# * Copyright (C) 2012-2015 Daniel Mueller (deso@posteo.net)                *\
"""
COPYRIGHT_DESO_LINE2 = """\
# * Copyright (C) 1991 Daniel Mueller (deso@posteo.net)                     *\
"""
COPYRIGHT_DESO_LINE2_FIXED = """\
# * Copyright (C) 1991,2015 Daniel Mueller (deso@posteo.net)                *\
"""


COPYRIGHT_CUSTOM_TEMPLATE = """\
/*
@(#)File:           $RCSfile: file.c,v $
@(#)Version:        $Revision: 1.00 $
@(#)Last changed:   $Date: 2015/09/11 $
@(#)Purpose:        Testing
@(#)Author:         XYZ
%s
@(#)Product:        :PRODUCT:
*/\
"""
COPYRIGHT_CUSTOM_LINE = """\
@(#)Copyright:      (C) XYZ\t1988-1991,\t2005-2010\
"""
COPYRIGHT_CUSTOM_LINE_FIXED = """\
@(#)Copyright:      (C) XYZ\t1988-1991,2005-2010,2015\
"""


COPYRIGHT_WITH_CONTENT = """\
/*
%s
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 */\
"""
COPYRIGHT_WITH_CONTENT_LINE = """\
 * Copyright (c) 2006 deso\
"""
COPYRIGHT_WITH_CONTENT_LINE_FIXED = """\
 * Copyright (c) 2006,2015 deso\
"""


class TestNormalize(TestCase):
  """Tests for the copyright year string normalization script."""
  def writeRunReadVerify(self, content, expected, policy=None, year=None):
    """Write some data into a temporary file, run normalize, and verify expected result."""
    with NamedTemporaryFile(buffering=0) as f:
      f.write(content.encode("utf-8"))
      f.seek(0)

      argv = [sysargv[0], f.name]
      if policy is not None:
        argv += ["--policy=%s" % policy]
      if year is not None:
        argv += ["--year=%d" % year]

      normalizeMain(argv)
      self.assertEqual(f.read(), expected.encode("utf-8"))


  def testNormalizeCopyrightYears(self):
    """Verify that copyright years are normalized properly."""
    # Tuples of <input>,<expected-output> strings.
    MSFT = (COPYRIGHT_MSFT_TEMPLATE % COPYRIGHT_MSFT_LINE,
            COPYRIGHT_MSFT_TEMPLATE % COPYRIGHT_MSFT_LINE_FIXED)
    VMW = (COPYRIGHT_VMW_TEMPLATE % COPYRIGHT_VMW_LINE,
           COPYRIGHT_VMW_TEMPLATE % COPYRIGHT_VMW_LINE_FIXED)
    GENTOO = (COPYRIGHT_GENTOO_TEMPLATE % COPYRIGHT_GENTOO_LINE,
              COPYRIGHT_GENTOO_TEMPLATE % COPYRIGHT_GENTOO_LINE_FIXED)
    CUSTOM = (COPYRIGHT_CUSTOM_TEMPLATE % COPYRIGHT_CUSTOM_LINE,
              COPYRIGHT_CUSTOM_TEMPLATE % COPYRIGHT_CUSTOM_LINE_FIXED)

    for content, expected in (MSFT, VMW, GENTOO, CUSTOM):
      self.writeRunReadVerify(content, expected, year=2015)


  def testNormalizeCopyrightYearsWithoutExtension(self):
    """Verify the current year is not included unless wanted."""
    GENTOO = (COPYRIGHT_GENTOO_TEMPLATE % COPYRIGHT_GENTOO_LINE,
              COPYRIGHT_GENTOO_TEMPLATE % COPYRIGHT_GENTOO_LINE_FIXED_NO_2015)

    for content, expected in (GENTOO, ):
      self.writeRunReadVerify(content, expected)


  def testNormalizeCopyrightYearsInMultipleHeaders(self):
    """Verify that multiple copyright headers are normalized correctly."""
    MSFT = COPYRIGHT_MSFT_TEMPLATE % COPYRIGHT_MSFT_LINE
    MSFT_FIXED = COPYRIGHT_MSFT_TEMPLATE % COPYRIGHT_MSFT_LINE_FIXED
    VMW = COPYRIGHT_VMW_TEMPLATE % COPYRIGHT_VMW_LINE
    VMW_FIXED = COPYRIGHT_VMW_TEMPLATE % COPYRIGHT_VMW_LINE_FIXED
    COPYRIGHT_MULTI_HEADER = "%s\n%s\n" % (MSFT, VMW)
    COPYRIGHT_MULTI_HEADER_FIXED = "%s\n%s\n" % (MSFT_FIXED, VMW_FIXED)

    content = COPYRIGHT_MULTI_HEADER
    expected = COPYRIGHT_MULTI_HEADER_FIXED
    self.writeRunReadVerify(content, expected, year=2015)


  def testNormalizeWithPadding(self):
    """Test for normalization with the 'pad' policy."""
    # Tuples of <input>,<expected-output> strings.
    DESO1 = (COPYRIGHT_DESO_TEMPLATE % COPYRIGHT_DESO_LINE1,
             COPYRIGHT_DESO_TEMPLATE % COPYRIGHT_DESO_LINE1_FIXED)
    DESO2 = (COPYRIGHT_DESO_TEMPLATE % COPYRIGHT_DESO_LINE2,
             COPYRIGHT_DESO_TEMPLATE % COPYRIGHT_DESO_LINE2_FIXED)

    for content, expected in (DESO1, DESO2):
      self.writeRunReadVerify(content, expected, policy="pad", year=2015)


  def testNormalizeFileWithContent(self):
    """Verify that copyright years are normalized properly."""
    content = COPYRIGHT_WITH_CONTENT % COPYRIGHT_WITH_CONTENT_LINE
    expected = COPYRIGHT_WITH_CONTENT % COPYRIGHT_WITH_CONTENT_LINE_FIXED

    self.writeRunReadVerify(content, expected, year=2015)


if __name__ == "__main__":
  main()
