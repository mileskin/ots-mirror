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
"""
OTS 0.1 compatible Result backend interface for qa-reports tool
"""
from ots.qareports_plugin.qareports_client import send_files
from ots.common.results.result_backend import ResultBackend

class QAReportsBackend(ResultBackend):
    """
    OTS 0.1 compatible Result backend interface for qa-reports tool
    """

    def __init__(self,
                 qa_hwproduct=None,
                 qa_testtype=None,
                 qa_target=None,
                 qa_release_version = None):
        """
        @type qa_hwproduct: C{string}
        @param qa_hwproduct: HW product used in the report

        @type qa_testtype: C{string}
        @param qa_testtype: Test Type used in the report

        @type qa_target: C{string}
        @param qa_target: Target used in the report
        
        @type qa_release_version: C{string}
        @param qa_release_version: Release_Version used in the report
        """

        self.result_xmls = []
        self.attachments = []
        self.hwproduct = qa_hwproduct
        self.testtype = qa_testtype
        self.target = qa_target
        self.release_version = qa_release_version
        self.disabled = False
        
    def name(self):
        """Returns the name of the backend"""
        return "QAReportsBackend"
    
    def process_raw_file(self, result_object, testrun_object):
        """This is called when raw file is sent to results plugin"""
        self.attachments.append((result_object.filename, result_object.content))

    def pre_process_xml_file(self, result_object, testrun_object):
        """This is called when starting to process new xml file"""
        self.result_xmls.append((result_object.filename, result_object.content))
        
        # Read input values from testrun object
        self.hwproduct =  testrun_object.get_option("qa_hwproduct")
        self.testtype = testrun_object.get_option("qa_testtype")
        self.target = testrun_object.get_option("qa_target")
        self.release_version = testrun_object.get_option("qa_release_version")

        # This option is mainly for testing and debugging
        self.disabled = \
            testrun_object.get_option("qa_reports_disabled") or False

    def finished_processing(self):
        """
        Send files to qa-reports from cmd line
        """
        if not self.disabled:
            send_files(self.result_xmls,
                       self.attachments,
                       hwproduct=self.hwproduct,
                       testtype=self.testtype,
                       target=self.target,
                       release_version = self.release_version)
            
