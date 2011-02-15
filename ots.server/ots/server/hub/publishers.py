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

"""
Publishers applies the Composite Pattern
to provide an interface to the Publisher Plugins
available to OTS 

The Exception Handling is as defined by 
SWALLOW_EXCEPTIONS
"""

#Python2.5 support
from __future__ import with_statement

import os
import traceback
import logging

from ots.common.framework.api import PublisherPluginBase
from ots.common.framework.api import plugins_iter
from ots.common.framework.api import plugin_exception_policy
from ots.common.dto.api import Monitor
from ots.server.distributor.api import DTO_SIGNAL


LOG = logging.getLogger(__name__)

################################
# PUBLISHERS
################################

class Publishers(PublisherPluginBase):
    """
    The Publishers Plugins 
    """

    #The policy for handling exceptions of the Publisher Plugins
    SWALLOW_EXCEPTIONS = True

    def __init__(self, request_id, testrun_uuid, 
                       sw_product, image, **kwargs):

        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param: The unique identifier for the testrun

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type image : C{str}
        @param image : The URL of the image
        """
        root_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        plugin_dir = os.path.join(root_dir, "plugins")
        self._publishers = []
        LOG.debug(root_dir)
        LOG.debug(plugin_dir)
        LOG.debug(plugins_iter(plugin_dir, "ots.publisher_plugin"))
        for publisher_klass in plugins_iter(plugin_dir, "ots.publisher_plugin"):
            LOG.info(plugin_dir)
            LOG.debug("Publisher found: '%s'"%(publisher_klass))
            with plugin_exception_policy(self.SWALLOW_EXCEPTIONS):
                publisher = publisher_klass(request_id,
                                        testrun_uuid, 
                                        sw_product, 
                                        image,
                                        **kwargs)
                LOG.debug("Adding publisher: '%s'"%(publisher))
                self._publishers.append(publisher)
        self._share_uris(testrun_uuid)
        
        DTO_SIGNAL.connect(self._callback)

    
    ##########################################
    # HELPERS
    ##########################################

    def _share_uris(self, testrun_uuid):
        """
        Share the URI information amongst all the loaded Publishers

        @type publishers : C{list} of C{ots.common.publisher_plugin_base}
        @param publishers : A list of all the PublisherPlugins
        """
        all_publisher_uris = {}
        for publisher in self._publishers:
            all_publisher_uris.update(publisher.get_this_publisher_uris())
        for publisher in self._publishers:
            publisher.set_all_publisher_uris(all_publisher_uris)

    def _delegator_iter(self, method_name, *args, **kwargs):
        """
        Call the `method_name` on all the registered publishers
        Exception Handling as dictated by policy

        @type : C{str}
        @param : The name of the method to call on the Publisher
        """
        LOG.debug("Delegating '%s' with args: '%s', kwargs: '%s'"
                   %(method_name, args, kwargs))
        for publisher in self._publishers:
            with plugin_exception_policy(self.SWALLOW_EXCEPTIONS):
                if hasattr(publisher, method_name):
                    method = getattr(publisher, method_name)
                    yield method(*args, **kwargs)

    def _callback(self, signal, dto, **kwargs):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type dto: L{ots.common.dto}
        @param dto: An OTS Data Transfer Object

        The callback for DTO_SIGNAL 
        Multimethod that delegates
        data to the handler depending on <type>
        """
        if isinstance(dto, Monitor):
            if dto.received is None:
                msg.set_received()
            self.set_monitors(dto)

    #############################################
    # Setters
    #############################################

    def set_expected_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that should have been run
        """
        list(self._delegator_iter("set_expected_packages", packages))
     
    def set_tested_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        list(self._delegator_iter("set_tested_packages", packages))
        
    def set_testrun_result(self, testrun_result):
        """
        @type testrun_result : C{str}
        @param testrun_result: The result of the Testrun
        """
        list(self._delegator_iter("set_testrun_result", testrun_result))
        
    def set_exception(self, exception):
        """
        @type: C{Exception}
        @param: The Exception raised by the Testrun 
        """
        list(self._delegator_iter("set_exception", exception))
        
    def set_results(self, results):
        """
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The results
        """
        list(self._delegator_iter("set_results", results))
        
    def set_monitors(self, monitor):
        """
        @type monitors : C{ots.common.dto.monitor}
        @param monitors : Monitor events for plugins
        """
        list(self._delegator_iter("set_monitors", monitor))
        
    ###########################################
    # Getters
    ###########################################

    def get_uris(self):
        """
        @rtype: C{dict} of C{str} : C{str}
        @rparam: A Dictionary of uris for the published data 
                 for the Publishers {name : uri} 
        """
        uris_dict_all = {}
        for uris_dict in self._delegator_iter("get_uris"):
            uris_dict_all.update(uris_dict)
        return uris_dict_all

    ##########################################
    # Publish 
    ##########################################

    def publish(self):
        """
        Publish the results of the Testrun
        """
        list(self._delegator_iter("publish"))
