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

from ots.common.plugin_base import PluginBase

class PublisherPluginBase(PluginBase):

    def __init__(self, request_id, sw_product, image):
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
        @type packages : C{ots.results.testrun_result
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

    def set_results(self, results):
        """
        @type results : C{ots.common.dto.results}
        @param results : The results
        """
        pass

    def set_delegated_parameters(self, **kwargs):
        """
        """
        #FIXME describe this
        pass

    def set_uris(self, uris_dict):
        """
        @type: C{dict} of C{str} : C{str}
        @param: A Dictionary of uris for the published data 
                for *all* Publishers in {name : uri} 
        """
        pass
        
    ###########################################
    # Getters
    ###########################################

    def get_uris(self):
        """
        @rtype: C{dict} of C{str} : C{str}
        @rparam: A Dictionary of uris for the published data 
                 for *this* Publisher in {name : uri} 
        """
        pass

    ##########################################
    # Publish 
    ##########################################

    def publish(self):
        """
        Publish the results of the Testrun
        """
        pass
