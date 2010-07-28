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

"""
Automated test for OTS Core functionality. 

Runs a remote_testrun on the OTS_Mock and check that the results files come back

Prerequisites:

 - Pyro results storage service running on Haloo 
 - RabbitMQ server running 
""" 

import os
import unittest 
import time

import multiprocessing
from minixsv import pyxsval as xsv

from ots.distributor.remote_testrun import _testrun_results_files_iter
from ots.distributor.remote_testrun import remote_testrun

import ots.worker
import ots.worker.tests
from ots.worker.api import worker_factory

def start_worker(config_filename):
    """
    Start the OTS Worker
    Helper for multiprocessing purposes
    """
    #Make sure ots_mock is on the PATH
    os.path.abspath(ots.distributor.__file__)
    dirname = os.path.dirname(os.path.abspath(ots.worker.__file__))
    os.path.join(dirname, "tests")
    mock_dir = os.path.join(dirname, "tests")
    new_path =  os.environ["PATH"] + ":" + mock_dir
    os.environ["PATH"] = new_path
    #
    worker = worker_factory(config_filename)
    worker.start()
   
class TestRemote(unittest.TestCase): 
     
    def setUp(self):
        self.worker_process = None

    def tearDown(self):
        if self.worker_process is not None:
            self.worker_process.terminate()
        #
        fqname = self._foo_fqname()
        if os.path.exists(fqname):
            os.unlink(fqname)

    ########################################
    # TESTS
    ########################################
        
    def test_remote_results_files_iter(self):
        class MockTestrun:
            def get_result_objects(self):
                class MockResult:
                    content = "foo"
                    def name(self):
                        return "mock"
                return [MockResult()]
        files = list(_testrun_results_files_iter(MockTestrun()))
        self.assertEquals(1, len(files))
        self.assertEquals("mock", files[0].name)
        self.assertEquals("foo", files[0].read())

    def test_remote(self):
        worker_config_filename = self._worker_config_filename()
        self.worker_process = multiprocessing.Process(target = start_worker,
                                                 args=(worker_config_filename,))
        self.worker_process.start()
        time.sleep(2)

        filename = "dummy_results_file.xml"
        distributor_config_filename = self._distributor_config_filename()
        results_files = remote_testrun(None, 
                                       distributor_config_filename, 
                                       "foo", 
                                       10, 
                                       111)

        self.assertEquals(1, len(results_files))        
        self.assertEquals(filename, results_files[0].name)
        self.assertEquals(self._dummy_results_xml(filename), 
                          results_files[0].read())
        start, end, junk = open(self._foo_fqname(), "r").read().split("\n")
        start, end = float(start), float(end)
        self.assertAlmostEquals(2, end-start, 1)

    def test_validate_schema(self):
        #Check that our test files comply with the schema
        dirname = os.path.dirname(os.path.abspath(ots.worker.tests.__file__))
        fqname = os.path.join(dirname, "data", "dummy_results_file.xml")
        testdefinition_xsd = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "testdefinition-results.xsd") 
        etw = xsv.parseAndValidateXmlInput(fqname, 
                                           testdefinition_xsd,
                                           xmlIfClass=xsv.XMLIF_ELEMENTTREE)
        et = etw.getTree()
        root = et.getroot()

        
    #################################
    # HELPERS
    #################################

    @staticmethod
    def _worker_config_filename():
        module = os.path.dirname(os.path.abspath(ots.worker.__file__))
        worker_config_filename = os.path.join(module, "config.ini")
        if not os.path.exists(worker_config_filename):
            raise Exception("%s not found"%(worker_config_filename))
        return worker_config_filename

    @staticmethod
    def _distributor_config_filename():
        dirname = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        distributor_config_filename = os.path.join(dirname, "config.ini")
        if not os.path.exists(distributor_config_filename):
            raise Exception("%s not found"%(distributor_config_filename))
        return distributor_config_filename
            
    @staticmethod
    def _foo_fqname():
        dirname = os.path.abspath(os.curdir)
        fqname = os.path.join(dirname, "foo")
        return fqname

    @staticmethod
    def _dummy_results_xml(filename):
        dirname = os.path.dirname(os.path.abspath(ots.worker.tests.__file__))
        fqname = os.path.join(dirname, "data", filename)
        return open(fqname, "r").read()
        
if __name__ == "__main__":
    unittest.main()
