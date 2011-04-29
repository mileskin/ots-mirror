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

"""
Example conductor plugin
"""

import logging
from ots.common.framework.api import ConductorPluginBase

LOG = logging.getLogger(__name__)


class ExampleConductorPlugin(ConductorPluginBase):
    """ Example Conductor Plugin """

    def __init__(self, options):
        """
        @type options: C{obj}
        @param options: Test run options in an
                        ots.worker.conductor.executor.TestRunData object
        """
        self.options = options

    def before_testrun(self):
        """
        Implement method to call your plug-in before a test run
        """
        LOG.info("ExampleConductorPlugin before_testrun " \
                  "method called.")

        raise NotImplementedError("Example conductor plug-in " \
            "before_testrun method not implemented.")

    def after_testrun(self):
        """
        Implement method to call your plug-in after a test run
        """
        LOG.info("ExampleConductorPlugin after_testrun " \
                  "method called.")

        raise NotImplementedError("Example conductor plug-in " \
            "after_testrun method not implemented.")

    def set_target(self, hw_target):
        """
        Implement set target method

        @type hw_target: C{ots.worker.conductor.testtarget.TestTarget}
        @param hw_target: Hardware specific communication class
        """
        LOG.info("ExampleConductorPlugin set_target " \
                  "method called.")

        raise NotImplementedError("Example conductor plug-in " \
            "set_target method not implemented.")

    def set_result_dir(self, result_dir):
        """
        Implement set result directory method

        @type result_dir: C{string}
        @param result_dir: Result file directory path
        """
        LOG.info("ExampleConductorPlugin set_result_dir " \
                  "method called.")

        raise NotImplementedError("Example conductor plug-in " \
            "set_result_dir method not implemented.")

    def get_result_files(self):
        """
        Implement get result files directory

        @rtype: C{list} of C{str}
        @rparam: A list of result file paths
        """
        LOG.info("ExampleConductorPlugin get_result_files method called.")

        raise NotImplementedError("Example conductor plug-in " \
            "get_result_files method not implemented.")
