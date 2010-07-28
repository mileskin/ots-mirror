"""
This post-process plugin takes care of fetching testrun data from info service
"""

# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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

#import logging 
import Pyro.errors
import Pyro.core

import copy

class InfoClient(object):
    """This plugin communicates with Info service"""
        
    def __init__(self, host, port, log, service_proxy=None):
        self.log = log
        self.hostname = host
        self.port = int(port)
        self.client_initialized = False
       
        if not service_proxy:
            service_proxy = self._get_server_proxy("info")
        self.service = service_proxy

        
    def name(self):
        """Returns the name of the backend"""
        return "InfoClient"

##
#
# Generic info service access methods:
#
##

    def add_testrun(self, testrun_object):
        """Adds testrun to info service"""
        
        self.service.add_testrun(testrun_object.get_testrun_data())

        self.log.info("Added testrun %s to info service" %
                      str(testrun_object.get_testrun_id()))

    def remove_testrun(self, testrun_id):
        """Remove testrun from info service"""
        self.service.remove_testrun(testrun_id)
        self.log.info("Removed testrun %s from info service" % str(testrun_id))


    def get_testrun(self, testrun_id):
        """Returns the testrundata object for the testrun_id"""
        return self.service.get_testrun(testrun_id)


    def get_state(self, testrun_id):
        """
        Returns the testrun state as a tuple. First element
        contains fixed state string and the second a 
        additional state info 

        Possible state values:
        NOT_STARTED,
        QUEUED,
        TESTING,
        FLASHING,
        STORING_RESULTS,
        FINISHED
        """
        return self.service.get_state(testrun_id)

    def set_state(self, testrun_id, state, status_info=""):
        """
        Sets state of the testrun. state is a fixed state string
        and status info a free additional status info
        
        Possible state values:
        NOT_STARTED,
        QUEUED,
        TESTING,
        FLASHING,
        STORING_RESULTS,
        FINISHED
        """
        self.service.set_state(testrun_id, state, status_info)


    def get_result(self, testrun_id):
        """
        Returns (result, error_info) as a tuple of two strings.
        Possible values for result:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')
        """
        return self.service.get_result(testrun_id)


##
# 
# Post process plugin interface:
#
##

    def process(self, testrun_object):
        """
        Fetches testrun data from info service and updates testrun_object.
        
        NOTE: So far updating is implemented for the following data only:
                testpackagedata
                executed_packages
                state
                status_info
                result
                error_info
                error_code
        """

        self.log.info("Fetching testrun data from info service")
        testrun_id = testrun_object.get_testrun_id()
        
        for data in self.service.get_all_package_data(testrun_id):
            testrun_object.add_testpackage_data(data)

        packages_dict = self.service.get_all_executed_packages(testrun_id)

        testrun_object.set_all_executed_packages( copy.deepcopy(packages_dict) )

        state, status_info = self.service.get_state(testrun_id)
        testrun_object.set_state(state, status_info)

        result = self.service.get_result(testrun_id)

        #error_info and error_code are meaningless in info service (typically 
        #empty strings) unless if there actually is an error to be reported. 
        #That's why they should be copied to testrun only in case of error.
        #If testrun result is already set to error, let's keep first occurrence.
        if result == "ERROR" and testrun_object.get_result() != "ERROR":
            testrun_object.set_result(result)
            testrun_object.set_error_info(self.service.get_error_info(testrun_id))
            testrun_object.set_error_code(self.service.get_error_code(testrun_id))

        self.log.info("Fetching testrun data done.")

        
##
#
# Private methods:
#
##

    
    def _get_server_proxy(self, service):
        """Gets proxy for service object"""
        
        if not self.client_initialized:
            Pyro.core.initClient()
            self.client_initialized = True

        try:
            URI = 'PYROLOC://%s:%d/%s' % (self.hostname, self.port, service)
            return Pyro.core.getAttrProxyForURI(URI)

        except Pyro.core.PyroError, x:
            raise Pyro.core.PyroError("Couldn't bind object, Pyro says:", x)



