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


"""This file contains an abstract base class for xml handler backends"""

class ResultBackend(object):
    """
    An abstract base class for xml handler backends. If you want to implement
    your own ResultBackend, just subclass this and reimplement the methods you
    need.
    """

    def __init__(self):
        self.plugin_name = "ResultBackend"
    
        
    def name(self):
        """Returns the name of the backend"""
        return self.plugin_name

    def started_processing(self, testrun_object):
        """This is called when processing of result files starts"""

    
    def process_raw_file(self, result_object, testrun_object):
        """This is called when raw file is sent to results plugin"""

    def pre_process_xml_file(self, result_object, testrun_object):
        """This is called when starting to process new xml file"""
        
    def pre_process_test_results(self, values):
        """This is called when starting to process a test results"""
    
    def pre_process_suite(self, values):
        """This is called when starting to process a suite"""

    def pre_process_set(self, values):
        """This is called when starting to process a set"""

    def pre_process_case(self, values):
        """This is called when starting to process a case"""

    def pre_process_step(self, values):
        """This is called when starting to process a step"""

    def post_process_xml_file(self):
        """This is called when finished processing new xml file"""
        
    def post_process_test_results(self):
        """This is called when finished processing a test results"""
    
    def post_process_suite(self):
        """This is called when finished processing a suite"""

    def post_process_set(self):
        """This is called when finished processing a set"""

    def post_process_case(self):
        """This is called when finished processing a case"""

    def post_process_step(self):
        """This is called when finished processing a step"""

    def finished_processing(self):
        """This is called when all files are processed"""
