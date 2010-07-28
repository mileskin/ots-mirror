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

import unittest

import logging

from ots.distributor.testrundata import TestrunData
from ots.distributor.testrun import Testrun

from ots.pyro_clients.infoclient import InfoClient
from ots.pyro_clients.resultstorageclient import ResultsStorageClient

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',)

log = logging.getLogger()        

class testResultStorageClient(unittest.TestCase):
    """unit tests for ResultStorageClient"""



    def setUp(self):
        host = "localhost"
        port = 1982
        self.service = ResultStorageStub() 
        self.client = ResultsStorageClient(host, port, log, self.service) 


        
    def tearDown(self):
        pass


    def testName(self):
        self.assertEquals(self.client.name(), "ResultStorageClient")


    def testprocess(self):
        testrun_object = TestrunStub()
        self.client.process(testrun_object)
        self.assertEquals(testrun_object.results[0].content, "joo")

    def testResultsAreCleanedFromService(self):
        testrun_object = TestrunStub()
        self.client.process(testrun_object)
        self.assertEquals(self.service.cleaned, True)


class ResultObjectStub(object):
    def __init__(self):
        self.content = "joo"


class ResultStorageStub(object):
    def __init__(self):
        self.cleaned = False

    def get_results(self, testrun_id):
        return [ResultObjectStub()]
    
    def clean_testrun_results(self, testrun_id):
        self.cleaned = True

class TestrunStub(object):
    def __init__(self):
        self.results = []

    def add_result_object(self, file):
        self.results.append(file)

    def get_testrun_id(self):
        return 666

log = logging.getLogger()        
class testInfoClient(unittest.TestCase):
    """unit tests for InfoClient"""



    def setUp(self):

        self.infoservice = InfoServiceStub()
        self.infoclient = InfoClient("localhost", 1982, log, self.infoservice) 


        
    def tearDown(self):
        pass


    def testAddTestrunToInfoService(self):
        build_id = 66666
        testrun_id = 55

        testrun_object = Testrun()
        testrun_object.set_testrun_id(testrun_id)
        testrun_object.set_request_id(build_id)
 
        self.infoclient.add_testrun(testrun_object)
        self.assertEquals(self.infoservice.testruns[testrun_id].get_build_id(), build_id)


    def testRemoveTestrunFromInfoService(self):
        

        testrun_object = self.create_testrun_object()
        self.infoclient.add_testrun(testrun_object)
        self.failIf(testrun_object.get_testrun_id() not in self.infoservice.testruns.keys())
        self.infoclient.remove_testrun(testrun_object.get_testrun_id())
        self.failIf(testrun_object.get_testrun_id() in self.infoservice.testruns.keys())

    def testGetTestrunFromInfoService(self):
        

        testrun_object = self.create_testrun_object()
        self.infoclient.add_testrun(testrun_object)
        self.failIf(testrun_object.get_testrun_id() not in self.infoservice.testruns.keys())
        testrun_data = self.infoclient.get_testrun(testrun_object.get_testrun_id())
        self.assertEquals(testrun_data.get_build_id(), testrun_object.get_request_id())


    def testProcess(self):
        """
        Test for process() method. Checks if the testrun_object given to
        process() gets all the data from info service. 

        Result in info service stub is set to ERROR and in testrun result is 
        NOT_READY, thus enabling copying of error info and error code as well.
        """
        pkg_data1 = TestPackageDataStub()
        pkg_data2 = TestPackageDataStub()
        pkg_list1 = ["env1-executedpkg1", "env1-executedpkg2"]
        pkg_list2 = ["env2-executedpkg1", "env2-executedpkg2"]
        all_pkgs = dict()
        env1 = "hardware"
        env2 = "scratchbox"
        all_pkgs[env1] = pkg_list1
        all_pkgs[env2] = pkg_list2

        self.infoservice.add_package_data(55, "pkg1", pkg_data1)
        self.infoservice.add_package_data(55, "pkg2", pkg_data2)

        self.infoservice.add_executed_packages(55, env1, pkg_list1)
        self.infoservice.add_executed_packages(55, env2, pkg_list2)

        testrun_object = Testrun()
        testrun_object.set_testrun_id(55)

        self.assertEquals(testrun_object.get_all_testpackage_data(), [])
        packages = testrun_object.get_all_executed_packages()
        self._assert_equals_executed_packages(packages, all_pkgs)
        
        self.infoclient.process(testrun_object) #this moves the data

        self.assertTrue(pkg_data1 in testrun_object.get_all_testpackage_data())
        self.assertTrue(pkg_data2 in testrun_object.get_all_testpackage_data())

        packages = testrun_object.get_all_executed_packages()
        self._assert_equals_executed_packages(packages, all_pkgs)

        self.assertEquals(testrun_object.get_state(), self.infoservice.get_state(55))
        self.assertEquals(testrun_object.get_result(), self.infoservice.get_result(55))
        self.assertEquals(testrun_object.get_error_info(), self.infoservice.get_error_info(55))
        self.assertEquals(testrun_object.get_error_code(), self.infoservice.get_error_code(55))


    def testProcess_with_error_result(self):
        """
        Test for process() method. 
        Verifies that infoclient cannot overwrite error information in testrun.
        """
        pkg_data1 = TestPackageDataStub()

        self.infoservice.add_package_data(55, "pkg1", pkg_data1)

        testrun_object = Testrun()
        testrun_object.set_testrun_id(55)
        testrun_object.set_result("ERROR")
        testrun_object.set_error_info("first error")
        testrun_object.set_error_code("777")

        self.infoclient.process(testrun_object)

        self.assertEquals(testrun_object.get_result(), "ERROR")
        self.assertEquals(testrun_object.get_error_info(), "first error")
        self.assertEquals(testrun_object.get_error_code(), "777")



#
# Test utility methods:
#

    def _assert_equals_executed_packages(self, dict1, dict2):
        #simple comparison between dicts would only compare dictionary lenghts!
        for env in dict1.keys():
            self.assertEquals(dict1[env], dict2[env])


    def create_testrun_object(self):
        """Creates a testrun object with build_id and testrun_id"""
        build_id = 66666
        testrun_id = 55

        testrun_object = Testrun()
        testrun_object.set_testrun_id(testrun_id)
        testrun_object.set_request_id(build_id)
        return testrun_object






class InfoServiceStub(object):
    def __init__(self):
        self.testruns = {}
        self.package_data = []
        self.state = ("NOT_STARTED","joo")
        self.result = "ERROR"
        self.error_info = "my string"
        self.error_code = "123"
        self.executed_packages = dict()
    def add_testrun(self, testrun):
        self.testruns[int(testrun.get_testrun_id())] = testrun
    def remove_testrun(self, testrun_id):
        del self.testruns[testrun_id]
    def get_testrun(self, testrun_id):
        data = TestrunData()
        data.set_testrun_id(55)
        data.set_build_id(66666)
        return data

    def add_package_data(self, testrun_id, test_package, data):
        self.package_data.append(data)

    def get_all_package_data(self, testrun_id):
        return self.package_data

    def add_executed_packages(self, testrun_id, environment, packages):
        self.executed_packages[environment] = packages

    def get_all_executed_packages(self, testrun_id):
        return self.executed_packages
    
    def get_state(self, testrun_id):
        return self.state

    def get_result(self, testrun_id):
        return self.result

    def get_error_info(self, testrun_id):
        return self.error_info

    def get_error_code(self, testrun_id):
        return self.error_code


class TestPackageDataStub(object):
    def __init__(self):
        self.name = "joo"


    
if __name__ == '__main__':
    unittest.main()
