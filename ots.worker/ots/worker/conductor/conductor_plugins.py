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

"""
ConductorPlugins applies the Composite Pattern to provide an interface
to the Conductor Plug-ins

The Exception Handling is as defined by SWALLOW_EXCEPTIONS
"""

#Python2.5 support
from __future__ import with_statement

import os
import logging

from ots.common.framework.api import ConductorPluginBase
from ots.common.framework.api import plugins_iter
from ots.common.framework.api import plugin_exception_policy


LOG = logging.getLogger(__name__)

################################
# CONDUCTOR PLUGINS
################################

class ConductorPlugins(ConductorPluginBase):
    """
    The Conductor Plugins 
    """

    # The policy for handling exceptions of the Conductor Plugins
    SWALLOW_EXCEPTIONS = True

    def __init__(self, options):
        """
        ConductorPlugins initialization

        @type options: C{Object}
        @param options: TestRunData object
        """
        root_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        plugin_dir = os.path.join(root_dir, "plug-ins")
        self._plugins = []
        LOG.debug("plugin_dir: %s" % plugin_dir)
        LOG.debug(plugins_iter(plugin_dir, "ots.plugin.conductor"))
        for plugin_klass in plugins_iter(plugin_dir, "ots.plugin.conductor"):
            LOG.debug("Conductor plug-in found: '%s'" % plugin_klass)
            with plugin_exception_policy(self.SWALLOW_EXCEPTIONS):
                plugin = plugin_klass(options)
                LOG.debug("Adding a conductor plug-in: '%s'" % plugin)
                self._plugins.append(plugin)

    ##########################################
    # HELPERS
    ##########################################

    def _delegator_iter(self, method_name, *args, **kwargs):
        """
        Call the `method_name` on all the registered conductor plug-ins
        Exception Handling as dictated by policy

        @type : C{String}
        @param : The name of the method to call on the plug-in
        """
        LOG.debug("Delegating '%s' with args: '%s', kwargs: '%s'"
                   %(method_name, args, kwargs))
        for plugin in self._plugins:
            with plugin_exception_policy(self.SWALLOW_EXCEPTIONS):
                if hasattr(plugin, method_name):
                    method = getattr(plugin, method_name)
                    yield method(*args, **kwargs)

    ##########################################
    # Public methods
    ##########################################

    def before_testrun(self):
        """
        Call the conductor plug-in before a test run is started
        """
        list(self._delegator_iter("before_testrun"))

    def after_testrun(self):
        """
        Call the conductor plug-in after a test run has ended
        """
        list(self._delegator_iter("after_testrun"))

    ##########################################
    # Setters
    ##########################################

    def set_target(self, hw_target):
        """
        Set hardware target

        @type hw_target: C{ots.worker.conductor.testtarget.TestTarget}
        @param hw_target: Hardware specific communication class
        """
        list(self._delegator_iter("set_target", hw_target))

    def set_result_dir(self, result_dir):
        """
        Set result file directory

        @type result_dir: C{String}
        @param result_dir: Result file directory path
        """
        list(self._delegator_iter("set_result_dir", result_dir))

    ##########################################
    # Getters
    ##########################################

    def get_result_files(self):
        """
        Get result file paths

        @rtype C{List}
        @rparam List of all result file paths
        """
        all_result_files = []
        for files in self._delegator_iter("get_result_files"):
            if type(files) == list:
                all_result_files.extend(files)
        return all_result_files
