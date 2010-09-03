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

from ots.common.packages import ExpectedPackages, TestedPackages
from ots.results.go_nogo_gauge import PackageException, _check_run_validity

class TestGoNoGoGauge(unittest.TestCase):
    
    def test_no_packages(self):
        self.assertRaises(PackageException,
                          _check_run_validity,
                          [], True, True, [])

    def test_host_testing_enabled(self):
        ep = ExpectedPackages("hardware", [])
        self.assertRaises(PackageException,
                          _check_run_validity,
                          [ep], False, True, [])

    def test_hardware_enabled(self):
        ep = ExpectedPackages("host.foo", [])
        self.assertRaises(PackageException,
                          _check_run_validity,
                          [ep], True, False, [])

    def test_package_results_exists_for_environment_package(self):
        ep = ExpectedPackages("host.foo", [])
        self.assertRaises(PackageException,
                          _check_run_validity,
                          [ep], False, True, [])


    def test_package_results_validate(self):
        ep = ExpectedPackages("host.foo", [])
        tp = TestedPackages("host.foo", [])
        _check_run_validity([ep], False, True, [tp])
    
if __name__ == "__main__":
    unittest.main()
