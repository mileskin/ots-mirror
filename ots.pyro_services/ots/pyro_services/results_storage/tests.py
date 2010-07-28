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
from ots.pyro_services.results_storage import resultobject
from ots.pyro_services.results_storage.results_storage import ResultsStorage
from ots.pyro_services.results_storage import resultobject



class TestResultsStorage(unittest.TestCase):
    
    def setUp(self):
        self.host = "localhost"
        self.port = 6666
        config = {'cleanup_period': 60}
        self.storage = ResultsStorage(config, self.host, self.port)
        logging.basicConfig(level = logging.DEBUG)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    def testInfo(self):
        info = self.storage.info()
        expected_info = "OTS Results Storage Service running at "+self.host
        
        self.assertEquals(info, expected_info)
        
        
    def testAddResult(self):
        
        testrun_id = 666
        filename = "testfile.txt"
        content = "testcontent"
        self.storage.add_result(testrun_id, filename, content)
        results = self.storage.get_results(testrun_id)
        self.assertEquals(results[0].get_content(), content)
        

    def testAddResultObject(self):
        testrun_id = 666
        filename = "testfile.txt"
        content = "testcontent"
        results_object = resultobject.ResultObject(filename, content)
        self.storage.add_results_object(testrun_id,results_object)
        results = self.storage.get_results(testrun_id)
        self.assertEquals(results[0].get_content(), content)


    def testGetResultsWithNonexistingTestrun(self):
        results = self.storage.get_results(12345345345)
        self.assertFalse(results)

    def testWithMultipleResultFiles(self):
        
        testrun_id = 666
        filename1 = "testfile1.txt"
        content1 = "testcontent1"

        filename2 = "testfile2.txt"
        content2 = "testcontent2"

        self.storage.add_result(testrun_id, filename1, content1)        
        self.storage.add_result(testrun_id, filename2, content2)

        results = self.storage.get_results(testrun_id)

        self.assertEquals(results[0].get_content(), content1)
        self.assertEquals(results[1].get_content(), content2)
        
    def testWithSameFilesFromHwAndSB(self):
        
        testrun_id = 666
        filename1 = "testfile1.txt"
        content1 = "testcontent1"

        self.storage.add_result(testrun_id, filename1, content1, origin="", testpackage="something-tests", environment="hardware")        
        self.storage.add_result(testrun_id, filename1, content1, origin="", testpackage="something-tests", environment="scratchbox")
        
        results = self.storage.get_results(testrun_id)
        

        self.assertEquals(results[0].get_content(), content1)
        self.assertEquals(results[1].get_content(), content1)
  

    def testWithMultipleTestruns(self):
        
        testrun_id1 = 666
        filename1 = "testfile1.txt"
        content1 = "testcontent1"

        testrun_id2 = 667
        filename2 = "testfile2.txt"
        content2 = "testcontent2"

        self.storage.add_result(testrun_id1, filename1, content1)        
        self.storage.add_result(testrun_id2, filename2, content2)

        results1 = self.storage.get_results(testrun_id1)
        results2 = self.storage.get_results(testrun_id2)
        
        self.assertEquals(results1[0].get_content(), content1)
        self.assertEquals(results2[0].get_content(), content2)
        self.assert_(filename2 not in results1)        
        self.assert_(filename1 not in results2)        

    def testCleanTestrunResults(self):
        
        testrun_id1 = "666"
        filename1 = "testfile1.txt"
        content1 = "testcontent1"

        self.storage.add_result(testrun_id1, filename1, content1)        
        self.storage.clean_testrun_results(testrun_id1)
        results1 = self.storage.get_results(testrun_id1)

        self.assertEquals(results1, [])

    def testCleanFilesOlderThan(self):
        
        testrun_id1 = "666"
        filename1 = "testfile1.txt"
        content1 = "testcontent1"

        testrun_id2 = "667"
        filename2 = "veryoldfile.txt"
        content2 = "testcontent2"

        results_object1 = resultobject.ResultObject(filename1, content1)
        results_object2 = resultobject.ResultObject(filename2, content2)

        # Modify timestamp to make the other file older
        results_object2.timestamp = results_object2.timestamp - (5*24*60*60) # 5 days
        
        self.storage.add_results_object(testrun_id1, results_object1)
        self.storage.add_results_object(testrun_id2, results_object2)

        self.storage.clean_files_older_than(3*24) # 3 days
        results1 = self.storage.get_results(testrun_id1)
        results2 = self.storage.get_results(testrun_id2)

        self.assertEquals(results1[0].get_content(), content1)
        self.assertEquals(results2, [])

#TODO: Move to separate file. (manual_tests.py)

    def donottestOverPyro(self): # Manual test. Requires running results server.
        storage = self._getStorage()  
        testrun_id = 666
        filename = "testfile.txt"
        content = "testcontent"
        storage.add_result(testrun_id, filename, content)
        results = storage.get_results(testrun_id)
        self.assertEquals(results[filename].get_content(), content)


    def donottestLoadOverPyro(self): # Manual test. Requires running server.
        storage = self._getStorage()
        import random  
        for id in range(1001):
            testrun_id = str(id)
            for resultfile in range(10): 
                filename = "testfile%d.txt" % random.randrange(0, 100000, 1)
                content = "testcontent%d." % random.randrange(0, 100000, 1)
                storage.add_result(testrun_id, filename, content)
                results = storage.get_results(testrun_id)
                self.assertEquals(results[filename].get_content(), content)

        
        
    def _getStorage(self):

        from Pyro.ext import remote_nons

#        SERVERHOST = "localhost"
        SERVERHOST = "haloo.research.nokia.com"
        SERVERPORT = 1982
        return remote_nons.get_server_object('results_storage',SERVERHOST, SERVERPORT)


if __name__ == '__main__':
    unittest.main()

