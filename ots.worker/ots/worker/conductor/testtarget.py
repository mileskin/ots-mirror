# -*- coding: utf-8 -*-
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

"""General test target"""

# Example test target, disable pylint warnings 
# pylint: disable=W0613

import logging

class TestTarget(object):
    """Base class for different types of test targets."""
    
    def __init__(self, testrun):
        self.log = logging.getLogger("conductor")
        self.testrun = testrun
        self.config = testrun.config

    def __str__(self):
        raise Exception("Error: not implemented")

    def prepare(self):
        """Flash the system under test"""
        raise Exception("Error: not implemented")

    def cleanup(self):
        """Clean up all temporary stuff used in setting up target. Optional"""
        pass

    def get_commands_to_show_test_environment(self):
        """
        List of commands to be executed in test environment to show information 
        about the environment. Must be list of tuples (X,Y) or empty list.
        X = The complete command to be executed at worker.
        Y = Plain command without test environment (SSH/SB) specific wrappings.
        """
        raise Exception("Error: not implemented")

    def get_command_to_copy_file(self, src_path, dest_path):
        """Command used to copy file"""
        raise Exception("Error: not implemented")

    def get_command_to_copy_testdef(self):
        """
        Command used to copy test definition. 
        Must be executable command or empty string.
        """
        raise Exception("Error: not implemented")

    def get_command_to_copy_results(self):
        """
        Command used to copy test results. 
        Must be executable command or empty string.
        """
        raise Exception("Error: not implemented")

    def get_command_to_find_test_packages(self):
        """Returns command that lists packages containing file tests.xml."""
        raise Exception("Error: not implemented")

    def get_command_to_list_installed_packages(self):
        """Returns command that lists all installed packages in target."""
        raise Exception("Error: not implemented")

    def parse_for_packages_with_file(self, lines):
        """
        Parse test package names from lines. Returns list of test packages.
        """
        raise Exception("Error: not implemented")

    def parse_installed_packages(self, lines):
        """
        Parse test package names from lines. Returns list of test packages.
        """
        raise Exception("Error: not implemented")

