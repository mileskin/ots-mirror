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

import unittest 

from ots.common.packages import PackagesBase, ExpectedPackages, TestedPackages

class TestPackages(unittest.TestCase):
    
    def test_is_host_test(self):
        pkgs = PackagesBase("environment", ["pkg1", "pkg2"])
        self.assertFalse(pkgs.is_host_tested)
        pkgs = PackagesBase("host.environment", ["pkg1", "pkg2"])
        self.assertTrue(pkgs.is_host_tested)

    def test_is_hardware(self):
        pkgs = PackagesBase("environment", ["pkg1", "pkg2"])
        self.assertFalse(pkgs.is_hw_tested)
        pkgs = PackagesBase("hardware", ["pkg1", "pkg2"])
        self.assertTrue(pkgs.is_hw_tested)

    def test_is_equals(self):
        pkg_1 = PackagesBase("environment", ["pkg1", "pkg2"])
        pkg_2 = PackagesBase("environment", ["pkg1", "pkg2"])
        pkg_3 = PackagesBase("environment", ["pkg1", "pkg3"])
        self.assertEquals(pkg_1, pkg_2)
        self.assertNotEquals(pkg_1, pkg_3)
       
if __name__ == "__main__":
    unittest.main()
