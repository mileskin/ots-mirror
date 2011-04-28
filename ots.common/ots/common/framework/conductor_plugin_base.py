# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

""" Interface class for Conductor plug-ins """

class ConductorPluginBase(object):
    """ Base class for Conductor plug-ins """

    def __init__(self, executor, options):
        """
        @type options: C{obj}
        @param options: Executor object
                        ots.worker.conductor.executor.Executor object

        @type options: C{obj}
        @param options: Test run options in an
                        ots.worker.conductor.executor.TestRunData object
        """
        pass

    ##########################################
    # Triggers
    ##########################################

    def before_testrun(self):
        """
        Method to be called before starting a test run
        """
        pass

    def after_testrun(self):
        """
        Method to be called after a test run has finished
        """
        pass

    ##########################################
    # Setters
    ##########################################

    def set_target(self, hw_target):
        """
        Set hardware target

        @type hw_target: C{ots.worker.conductor.testtarget.TestTarget}
        @param hw_target: Hardware specific communication class
        """
        pass

    def set_result_dir(self, result_dir):
        """
        Set result file directory

        @type result_dir: C{string}
        @param result_dir: Result file directory path
        """
        pass

    ##########################################
    # Getters
    ##########################################

    def get_result_files(self):
        """
        Get result file paths
        """
        pass
