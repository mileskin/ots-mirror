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

"""Testrun class encapsulates everything related to a testrun in Ots server."""
import logging
import datetime

from collections import defaultdict as defaultdict
from ots.distributor.testrundata import TestrunData

RESULT_VALUES = ('NOT_READY', 'PASS', 'FAIL', 'NO_CASES', 'ERROR')

class Testrun(object):
    """
    Testrun class. Holds all testrun specific data.
    """    
    def __init__(self):

        self.log = logging.getLogger(__name__)
        self.request_id = ""
        self.sw_product = ""
        self.sw_version = ""
        self.image_name = ""
        self.image_url = ""
        self.email = ""
        self.test_packages = []
        self.executed_packages = dict()  #key = environment name.
        self.cmt = ""
        self.starttime = datetime.datetime.now()
        self.endtime = None
        self.testrun_id = None
        self.result_links = []
        self.options = {}
        self.result_objects = []
        self.testpackagedata = []

        self.state = "NOT_STARTED"        
        self.status_info = "" # Status info string. Can contain any string.

        # Testrun result can be changed with set_result().
        # Once it's been set to PASS/FAIL/ERROR, it cannot be changed anymore,
        # except that it can be set to ERROR always.
        self.result = "NOT_READY" # NOT_READY/PASS/FAIL/NO_CASES/ERROR
        self.error_info = "" # Error info string. Can contain any string.
        self.error_code = ""

    def get_all_executed_packages(self):
        """
        Returns all test packages that the worker reported as to be executed.
        It's a dictionary: Key = environment name. Value = list of packages.
        """
        return self.executed_packages

    def set_all_executed_packages(self, packages):
        """
        Sets all executed test packages to dictionary given as parameter.

        @type packages: C{dictionary}
        @param packages: Dictionary with environment as key. Each value is
                         list of test package names.
        """
        self.executed_packages = packages
        self.log.debug("Executed packages set to %s" % packages)

    def set_executed_pkgs_from_lists(self, testpackages, environments):
        """
        Sets all executed test packages from two lists of equal length.

        @type testpackages: C{list}
        @param testpackages: List of test package names.

        @type environments: C{list}
        @param environments: List of test environment names.
        """
        if len(testpackages) != len(environments):
            raise Exception("Lengths of testpackages and environments do not "\
                            "match")

        packages = defaultdict(list)
        for pkg, env in zip(testpackages, environments):
            packages[env.lower()].append(pkg)
            
        self.set_all_executed_packages(packages)

    def get_result(self):
        """
        Returns testrun result value. Possible values:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')
        """
        return self.result

    def set_result(self, result):
        """
        Sets the testrun result. Possible values:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')

        Result can be set only if its previous value was NOT_READY, except
        that it can be set to ERROR always.
        Result cannot be changed once it's been set to NO_CASES/PASS/FAIL/ERROR.
        """
        if result not in RESULT_VALUES:
            raise ValueError

        if self.result in ("NOT_READY") or result == "ERROR":
            self.result = result
            self.log.info("Result set to %s" % self.result)
        else:
            self.log.debug("Denied attempt to set result from %s to %s" \
                            % (self.result, result))

    def get_error_info(self):
        """Returns error_info string"""
        return self.error_info

    def set_error_info(self, error_info):
        """Set error info string for the testrun"""
        if not self.error_info:
            self.error_info = error_info
            self.log.info('error_info set to "%s"' % self.error_info)
        else:
            self.log.debug("Denied attempt to set error info from %s to %s" \
                            % (self.error_info, error_info))


    def get_error_code(self):
        """Returns error_code"""
        return self.error_code

    def set_error_code(self, error_code):
        """Set error_code for the testrun"""
        self.error_code = error_code
        self.log.debug('error_code set to "%s"' % self.error_code)


    def get_state(self):
        """Returns the state of the testrun as a tuple."""
        return (self.state, self.status_info)

    def set_state(self, state, status_info):
        """Sets the state of the testrun."""
        self.state = state
        self.status_info = status_info
        self.log.info("State set to %s" % self.state)
        self.log.info('Status_info set to "%s"' % self.status_info)


    def add_testpackage_data(self, data):
        """
        Stores testpackagedata object into testrun.
        """
        self.testpackagedata.append(data)
        self.log.debug("Added TestPackageData for package %s" % data.name)
        #self.log.debug("%s" % str(data.toXMLs()))

    def get_all_testpackage_data(self):
        """Returns all testpackagedata objects as a dictionary"""
        return self.testpackagedata
        
    def get_testrun_data(self):
        """
        Returns the data of the testrun as a testrundata object
        """
        data_object = TestrunData()

        data_object.set_result(self.result)
        data_object.set_error_info(self.error_info)
        data_object.set_state(self.state)
        data_object.set_status_info(self.status_info)

        data_object.set_options(self.options)
        data_object.set_testrun_id(self.testrun_id)
        data_object.set_build_id(self.request_id)
        data_object.set_sw_product(self.sw_product)
        data_object.set_image_url(self.image_url)
        data_object.set_email_list(self.email)
        data_object.set_test_packages(self.test_packages)
        for pkg in self.testpackagedata:
            data_object.add_package_data(pkg.name, pkg)
        return data_object
    

    def get_result_links(self):
        """Returns result links as a list of tuples: ("text", "url")"""
        return self.result_links
    
    def add_result_link(self, text, link):
        """Stores a tc link"""
        self.result_links.append((text, link))

    def set_options(self, options):
        """Set options dictionary"""
        self.options.update(options)
        self.log.info("Updated options: %s" % self.options)

    def get_host_testpackages(self):
        """
        Returns host test package list. Host test packages can be set with
        set_options().
        """
        try:
            return self.options['hosttest']
        except (KeyError, TypeError):
            return []

    def get_timeout(self):
        """
        Returns global timeout (minutes) from options.
        """
        self.log.debug("timeout: %s" % self.options['timeout'])
        return int(self.options['timeout'])

    def email_enabled(self):
        """
        Returns True if email is enabled
        """
        try:
            return not self.options['email'].lower() == 'off'
        except (KeyError, TypeError):
            return True
        return True


    def get_emmc_url(self):
        """
        Returns emmcurl from options.
        """
        try:
            self.log.debug("emmcurl: %s" % self.options['emmcurl'])
            return self.options['emmcurl']
        except (KeyError, TypeError):
            self.log.debug("emmcurl: "" (default value)")
            return ""

    
    def hardware_testing_enabled(self):
        """
        Returns true if testrun has hardware testing enabled in options.
        """
        if self.image_url:
            return True
        else:
            return False

    def get_option(self, key):
        """
        Returns the value for option key.
        Empty string is returned if key is not found.
        """
        try:
            return self.options[key]
        except (KeyError, TypeError):
            return ""


    def get_testrun_id(self):
        return self.testrun_id
           
    def set_testrun_id(self, testrun_id):
        self.testrun_id = testrun_id
        self.log.info("Testrun ID set to %s" % self.testrun_id)


    def get_start_time(self):
        return self.starttime
    
    def get_end_time(self):
        return self.endtime

    def get_request_id(self):
        """returns build request id for the testrun"""
        return self.request_id
    
    def set_request_id(self, build_id):
        """sets request id for the testrun"""
        self.request_id = build_id
        self.log.debug("request_id set to %s" % build_id)

    def get_sw_product(self):
        """returns sw product"""
        return self.sw_product
    
    def set_sw_product(self, product):
        """sets sw product"""
        self.sw_product = product
        self.log.debug("sw_product set to %s" % product)

    def get_sw_version(self):
        """returns sw version"""
        return self.sw_version
    
    def set_sw_version(self, version):
        """sets sw version"""
        self.sw_version = version
        self.log.debug("sw_version set to %s" % version)

    def get_image_name(self):
        """returns image name"""
        return self.image_name
    
    def set_image_name(self, image):
        """sets image name"""
        self.image_name = image
        self.log.debug("Image name set to %s" % image)

    def get_image_url(self):
        """returns image url"""
        return self.image_url
    
    def set_image_url(self, image):
        """sets image url"""
        self.image_url = image
        self.log.debug("Image url set to %s" % image)

    def get_email_list(self):
        """returns email addresses as a list"""
        return self.email
    
    def set_email_list(self, email_list):
        """sets list of emails. Result mail will be send to these addresses"""
        self.email = email_list
        self.log.debug("Email list set to %s" % email_list)

    def get_testpackages(self):
        """returns test packages as a list"""
        return self.test_packages
    
    def set_testpackages(self, packages):
        """sets test package list"""
        self.test_packages = packages
        self.log.debug("Test packages set to %s" % packages)
    
    def get_cmt_version(self):
        """returns CMT version"""
        return self.cmt
    
    def set_cmt_version(self, version):
        """sets CMT version"""
        self.cmt = version
        self.log.debug("CMT version set to %s" % version)

    def get_device_group(self):
        """returns deviceGroup"""
        return self.options["device"]["devicegroup"]

    def add_result_object(self, result_object):
        """Stores a result object into testrun"""
        self.result_objects.append(result_object)

    def get_result_objects(self):
        """
        Returns all result objects stored into the testrun
        
        @rtype: C{list} consisting of L{ResultObject}
        @return: List of result objects

        """
        return self.result_objects
