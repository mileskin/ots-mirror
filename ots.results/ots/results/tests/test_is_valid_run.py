# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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

from ots.common.dto.api import Environment
from ots.results.is_valid_run import is_valid_run, PackageException
from ots.results.is_valid_run import _check_complete

class TestIsValidRun(unittest.TestCase):
    
    def test_no_packages(self):
        ep = {"ep" : []}
        tp = {"tp" : []}
        self.assertRaises(PackageException,
                          is_valid_run,
                          ep, tp, True, True)

    def test_hw_testing_enabled(self):
        ep = {Environment("host.foo") : ["pkg1", "pkg2"]}
        tp = {Environment("host.foo") : ["pkg1", "pkg2"]}
        self.assertRaises(PackageException,
                          is_valid_run,
                          ep, tp, True, False)

    def test_host_testing_enabled(self):
        ep = {Environment("hardware") : ["pkg1", "pkg2"]}
        tp = {Environment("host.foo") : ["pkg1", "pkg2"]}
        self.assertRaises(PackageException,
                          is_valid_run,
                          ep, tp, False, True)

    def test_chroot_testing_enabled(self):
        ep = {Environment("hardware") : ["pkg1", "pkg2"]}
        tp = {Environment("host.foo") : ["pkg1", "pkg2"]}
        self.assertRaises(PackageException,
                          is_valid_run,
                          ep, tp, False, False, True)

    def test_is_valid_run_all_environments(self):
        ep = {Environment("hardware") : ["pkg1"],
              Environment("host_hardware") : ["pkg1", "pkg2"],
              Environment("chroot") : ["pkg1", "pkg2", "pkg3"]}
        tp = {Environment("hardware") : ["pkg1"],
              Environment("host_hardware") : ["pkg1", "pkg2"],
              Environment("chroot") : ["pkg1", "pkg2", "pkg3"]}
        # No return value. Raises an exeption is something goes wrong
        self.assertEquals(is_valid_run(ep, tp, True, True, True), None)

    def test_is_valid_run_chroot_only(self):
        ep = {Environment("chroot") : ["pkg1", "pkg2"]}
        tp = {Environment("chroot") : ["pkg1", "pkg2"]}
        # No return value. Raises an exeption is something goes wrong
        self.assertEquals(is_valid_run(ep, tp, False, False, True), None)

    def test_check_complete(self):
        ep = {Environment("hardware") : ["hw_pkg1", "hw_pkg2"],
              Environment("host.foo") : ["pkg1", "pkg2", "pkg3"]}
        tp = {Environment("host.foo") : ["pkg1", "pkg2"]}
        self.assertRaises(PackageException,
                          _check_complete,
                          ep, tp)
        
if __name__ == "__main__":
    unittest.main()
