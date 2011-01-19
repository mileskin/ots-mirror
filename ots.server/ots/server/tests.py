# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

import os 
import glob 
import unittest
import pkg_resources

NAMESPACES = ["ots.server.hub", 
              "ots.server.allocator",
              "ots.server.distributor",
              "ots.server.xmlrpc"]

TESTS_DIRNAME = "tests"

FNAME_PATTERN = 'test_*.py'

def suite():
    s = unittest.TestSuite()
    for namespace in NAMESPACES:
        dirname = pkg_resources.resource_filename(namespace, TESTS_DIRNAME)
        fqnames = glob.glob(os.path.join(dirname,FNAME_PATTERN))
        for fqname in fqnames:
            ns = os.path.splitext(os.path.split(fqname)[1])[0]
            name = "%s.%s.%s"%(namespace, TESTS_DIRNAME, ns)
            __import__(name)
            suite = unittest.defaultTestLoader.loadTestsFromName(name)
            s.addTest(suite)
    return s
