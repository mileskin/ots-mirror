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

class QAReportsBackend():
    """
    OTS 0.1 compatible Result backend interface for qa-reports tool
    """

    def __init__(self):
        self.result_xmls = []
        self.attachments = []
    
        
    def name(self):
        """Returns the name of the backend"""
        return "QAReportsBackend"
    
    def process_raw_file(self, result_object, testrun_object):
        """This is called when raw file is sent to results plugin"""
        self.attachments.append(result_object)

    def pre_process_xml_file(self, result_object, testrun_object):
        """This is called when starting to process new xml file"""
        self.result_xmls.append(result_object)

    def finished_processing(self):
        """This is called when all files are processed"""
        
