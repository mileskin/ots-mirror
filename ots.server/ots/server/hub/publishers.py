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
"""

import os
import traceback
import logging

from ots.common.framework.api import PublisherPluginBase
from ots.common.framework.api import plugins_iter
from ots.common.framework.api import plugin_exception_policy

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
        for publisher_klass in plugins_iter(plugin_dir, "ots.publisher_plugin"):
            print publisher_klass
            try:
                publisher = publisher_klass(request_id,
                                        testrun_uuid, 
                                        sw_product, 
                                        image,
                                        **kwargs)
                LOG.debug("Adding publisher: '%s'"%(publisher))
                self._publishers.append(publisher)
            except Exception, err:
                LOG.debug("Error initialising Plugin")
                LOG.debug(traceback.format_exc())
        self._share_uris(testrun_uuid)
    
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


    def _safe_delegate_to_publishers(self, method_name, *args, **kwargs):
        """
        Call the `method_name` on all the registered publishers
        """
        for publisher in self._publishers:
            with plugin_exception_policy(self.SWALLOW_EXCEPTIONS):
                if hasattr(publisher, method_name):
                    method = getattr(publisher, method_name)
                    return method(*args, **kwargs)


    #############################################
    # Setters
    #############################################

    def set_expected_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that should have been run
        """
        return self._safe_delegate_to_publishers("set_expected_packages",
                                                 packages)
     
    def set_tested_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        return self._safe_delegate_to_publishers("set_tested_packages",
                                                 packages)

    def set_testrun_result(self, testrun_result):
        """
        @type packages : C{ots.results.testrun_result
        @param packages: The result of the Testrun
        """
        return self._safe_delegate_to_publishers("set_testrun_result",
                                                 testrun_result)

    def set_exception(self, exception):
        """
        @type: C{Exception}
        @param: The Exception raised by the Testrun 
        """
        return self._safe_delegate_to_publishers("set_exception",
                                                 testrun_result)

    def set_results(self, results):
        """
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The results
        """
        return self._safe_delegate_to_publishers("set_result",
                                                 testrun_result)

    def set_monitors(self, monitors):
        """
        @type monitors : C{list} of C{ots.common.dto.monitor}
        @param monitors : The monitors
        """
        return self._safe_delegate_to_publishers("set_monitors",
                                                 testrun_result)

    ###########################################
    # Getters
    ###########################################

    def get_uris(self):
        """
        @ytype: C{dict} of C{str} : C{str}
        @yparam: A Dictionary of uris for the published data 
                 for the Publishers {name : uri} 
        """
        for publisher in self._publishers:
            yield publisher.get_uris()
        
    ##########################################
    # Publish 
    ##########################################

    def publish(self):
        """
        Publish the results of the Testrun
        """
        return self._safe_delegate_to_publishers("publish",
                                                 testrun_result)
