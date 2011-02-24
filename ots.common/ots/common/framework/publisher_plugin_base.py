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

class PublisherPluginBase(object):

    def __init__(self, request_id, testrun_uuid, sw_product, image, **kwargs):
        pass

    #############################################
    # Setters
    #############################################

    def set_expected_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that should have been run
        """
        pass

    def set_tested_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        pass
        
    def set_testrun_result(self, testrun_result):
        """
        @type packages : C{ots.results.testrun_result}
        @param packages: The result of the Testrun
        """
        #FIXME move testrun result to common? 
        pass
    
    def set_exception(self, exception):
        """
        @type: C{Exception}
        @param: The Exception raised by the Testrun 
        """
        pass

    def set_test_definition_xml(self, test_definition):
        """
        @type test_definition : C{file}
        @param test_definition : The test definition xml
        """
        pass

    def set_all_publisher_uris(self, uris_dict):
        """
        @type: C{dict} of C{str} : C{str}
        @param: A Dictionary of uris for the published data 
                for *all* Publishers in {name : uri} 
        """
        pass

    def set_results(self, results):
        """
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The Results
        """
        pass

    def set_monitors(self, monitors):
        """
        @type monitors : C(list} of C{ots.common.dto.monitor}
        @param monitors : The Monitors
        """
        pass

    ###########################################
    # Getters
    ###########################################

    def get_this_publisher_uris(self):
        """
        @rtype: C{dict} of C{str} : C{str}
        @rparam: A Dictionary of uris for the published data 
                 for *this* Publisher in {name : uri} 
        """
        return {}

    ##########################################
    # Publish 
    ##########################################

    def publish(self):
        """
        Publish the results of the Testrun
        """
        pass
