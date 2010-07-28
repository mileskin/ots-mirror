"""Data structure class for testrun data"""

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

import time

STATE_VALUES = ("NOT_STARTED",
                "QUEUED",
                "TESTING",
                "FLASHING",
                "STORING_RESULTS",
                "FINISHED")

RESULT_VALUES = ('NOT_READY', 'PASS', 'FAIL', 'NO_CASES', 'ERROR')

class TestrunData(object):
    """TestrunData class. Holds testrun specific data."""

    # Disabling "too many public methods" warning.
    # This is a data container class and requires many get/set methods.
    # 
    # pylint: disable-msg=R0904

    def __init__(self):

        self.build_id = ""
        self.sw_product = ""
        self.name = ""
        self.image_url = ""
        self.rootstrap_url = ""
        self.email = []
        self.test_packages = ""
        self.executed_packages = dict()
        self.testrun_id = None
        self.result_links = []
        self.options = {}
        self.package_data = []
        self.created = time.time()

        self.state = "NOT_STARTED"
        self.status_info = "" # Status info string. Can contain any string
        self.result = "NOT_READY" # NOT_READY/PASS/FAIL/NO_CASES/ERROR
        self.error_info = "" # Error info string. Can contain any string
        self.error_code = ""

    def get_all_executed_packages(self):
        """
        Returns all test packages that the worker reported as to be executed.
        It's a dictionary: Key = environment name. Value = list of packages.
        """
        return self.executed_packages

    def add_executed_packages(self, environment, packages):
        """Stores a new list of test packages that will be / were executed."""
        self.executed_packages[environment] = packages

    def get_creation_time(self):
        """Returns testrundata creation time"""
        return self.created

    def add_package_data(self, test_package, data):
        """Stores TestPackageData object into testrun"""
        self.package_data.append(data)

    def get_package_data(self, test_package):
        """
        Returns TestPackageData object for a testpackage or None if
        data does not exist.
        """
        for pkg in self.package_data:
            
            if pkg.name == test_package:
                return pkg

        return None

    def get_all_package_data(self):
        """Returns all testpackagedata objects as a list"""
        return self.package_data
    
    def set_result(self, result):
        """
        Sets the testrun result. Possible values:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')

        Result can be set only if its previous value was NOT_READY or NO_CASES.
        Result cannot be changed once it's been set to PASS/FAIL/ERROR.
        """
        if result not in RESULT_VALUES:
            raise ValueError

        # This logic ensures that result can be set only once
        if self.result in ("NOT_READY", "NO_CASES"):
            self.result = result


    def get_result(self):
        """
        Returns testrun result value. Possible values:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')
        """
        return self.result


    def set_state(self, state):
        """
        Set testrun state. Possible values:
        NOT_STARTED,
        QUEUED,
        TESTING,
        FLASHING,
        STORING_RESULTS,
        FINISHED"""

        if state in STATE_VALUES:
            self.state = state
        else:
            raise ValueError
        
    def get_state(self):
        """
        Returns testrun state as a string. Possible values:
        NOT_STARTED,
        QUEUED,
        TESTING,
        FLASHING,
        STORING_RESULTS,
        FINISHED"""
        return self.state
    
    def set_status_info(self, status_info):
        """Update status info string for the testrun"""
        self.status_info = status_info

    def get_status_info(self):
        """Returns status info"""
        return self.status_info


    def set_error_info(self, error_info):
        """Set error info string for the testrun"""
        self.error_info = str(error_info)

    def get_error_info(self):
        """Returns error_info"""
        return self.error_info


    def get_error_code(self):
        """Returns error_code"""
        return self.error_code

    def set_error_code(self, error_code):
        """Set error code for the testrun"""
        self.error_code = str(error_code)


    def get_result_links(self):
        """Returns links to related result urls as a list of tuples: ("text", "url")"""
        return self.result_links
    
    def add_result_link(self, text, link):
        """Stores a result link"""
        self.result_links.append((text, link))

    def set_options(self, options):
        """
        Update options dictionary. Uses dict().update() so old values will
        be changed only if new options dictionary has them. 
        """
        self.options.update(options)

    def get_option(self, key):
        """Returns the value for option key.
           Empty string is returned if key is not found.
        """
        try:
            return self.options[key]
        except (KeyError, TypeError):
            return ""

    def get_testrun_id(self):
        return self.testrun_id
           
    def set_testrun_id(self, testrun_id):
        self.testrun_id = int(testrun_id)

    def get_build_id(self):
        """returns build id for the testrun"""
        return self.build_id
    
    def set_build_id(self, build_id):
        """sets build request id for the testrun"""
        self.build_id = int(build_id)

    def get_sw_product(self):
        """returns sw product"""
        return self.sw_product
    
    def set_sw_product(self, product):
        """sets sw product"""
        self.sw_product = product

    def get_name(self):
        """returns testrun name"""
        return self.name
    
    def set_name(self, name):
        """sets testrun name"""
        self.name = name

    def get_image_name(self):
        """returns image name"""
        return self.image_url.split("/")[-1]
    
    def get_image_url(self):
        """returns image url"""
        return self.image_url
    
    def set_image_url(self, image):
        """sets image url"""
        self.image_url = image

    def get_rootstrap_url(self):
        """returns rootstrap url"""
        return self.rootstrap_url
        
    def set_rootstrap_url(self, rootstrap):
        """sets rootstrap url"""
        self.rootstrap_url = rootstrap
        
    def get_email_list(self):
        """returns email addresses as a list"""
        return self.email
    
    def set_email_list(self, email_list):
        """sets email list"""
        self.email = email_list
        
    def get_test_packages(self):
        """returns test packages as a list"""
        return self.test_packages
    
    def set_test_packages(self, packages):
        """sets test package list"""
        self.test_packages = packages
        
