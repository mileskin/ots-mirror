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
Spike for OTS first iteration

Run a testrun remotely process the results
"""

# Disable pylint for bogus complaints
# pylint: disable-msg=E0611
# pylint: disable-msg=E0601

import logging 

from StringIO import StringIO

from ots.distributor.run_remote_process import run_remote_process
from ots.distributor.testrun import Testrun

from ots.pyro_clients.resultstorageclient import ResultsStorageClient

LOGGER = logging.getLogger(__name__)

###############################
# Pyro Results Storage Service
###############################

HOST = "haloo.research.nokia.com"
PORT = 1982

def _testrun_results_files_iter(testrun):
    """
    Generates the results files from the testrun object
    """
    for result in testrun.get_result_objects():
        output = StringIO()
        output.name = result.name()
        output.write(result.content)
        output.seek(0)
        yield output
    
def remote_testrun(test_definition, 
                   config_file, 
                   device_name, 
                   timeout, 
                   testrun_id):
    """
    Runs a mock job on a Worker

    @type test_definition: C{FIXME}
    @param test_definition: The test definition file

    @type config_file: C{string}
    @param config_file: The filepath of the config file #FIXME link to definition 

    @type device_name: C{string}
    @param device_name: The name of the device group (Routing Key for Worker)

    @type timeout: C{int}
    @param timeout: The timeout for the Task

    @type testrun_id : C{int}
    @param testrun_id: The unique number by which the testrun is identified

    @rtype: C{list} consisting of C{file} 
    @return: A List of Results Files
    """
    testrun = Testrun()
    testrun.set_testrun_id(testrun_id)
    COMMAND = "ots_mock foo 2 %s"% (testrun_id)#FIXME
    if run_remote_process(config_file, device_name, 
                          timeout, testrun_id, COMMAND):
        results_client = ResultsStorageClient(HOST, PORT, LOGGER)
        results_client.process(testrun)
        return list(_testrun_results_files_iter(testrun))
