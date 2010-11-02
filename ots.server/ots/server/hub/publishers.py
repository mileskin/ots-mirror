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

from ots.common.framework.api import  plugins_iter

class Publishers(object):

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

        @type delegated_params : C{dict}
        @param delegated_params : #FIXME
        """
        #FIXME: describe the intent behind kwargs 


        root_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        plugin_dir = os.path.join(root_dir, "plugins")
        self._publishers = []
        for publisher_klass in plugins_iter(plugin_dir, "ots.publisher_plugin"):
            publisher = publisher_klass(request_id,
                                        testrun_uuid, 
                                        sw_product, 
                                        image,
                                        **kwargs)
            self._publishers.append(publisher) 
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

    #############################################
    # Setters
    #############################################

    def set_expected_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that should have been run
        """
        for publisher in self._publishers:
            publisher.set_expected_packages(packages)

    def set_tested_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        for publisher in self._publishers:
            publisher.set_tested_packages(packages)

    def set_testrun_result(self, testrun_result):
        """
        @type packages : C{ots.results.testrun_result
        @param packages: The result of the Testrun
        """
        #FIXME move testrun result to common? 
        for publisher in self._publishers:
            publisher.set_testrun_result(testrun_result)

    def set_exception(self, exception):
        """
        @type: C{Exception}
        @param: The Exception raised by the Testrun 
        """
        for publisher in self._publishers:
            publisher.set_exception(exception)

    def set_results(self, results):
        """
        @type results : C{ots.common.dto.results}
        @param results : The results
        """
        for publisher in self._publishers:
            publisher.set_results(results)
        
    ###########################################
    # Getters
    ###########################################

    def get_uris(self):
        """
        @rtype: C{dict} of C{str} : C{str}
        @rparam: A Dictionary of uris for the published data 
                 for the Publishers {name : uri} 
        """
        for publisher in self._publishers:
            publisher.set_exception(packages)
        
    ##########################################
    # Publish 
    ##########################################

    def publish(self):
        """
        Publish the results of the Testrun
        """
        for publisher in self._publishers:
            publisher.publish()


