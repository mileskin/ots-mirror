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


import unittest
from ots.qareports_plugin.qareports_client import _generate_form_data

class test_qareports_client(unittest.TestCase):
    """unit tests for qareports_client"""


    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_generate_form_data_2_xml_2_attachments(self):
        report1 = ("name1", "content1")
        report2 = ("name2", "content2")
        attachment1 = ("attachment_name1", "attachment_content1")
        attachment2 = ("attachment_name2", "attachment_content2")
        files = _generate_form_data([report1, report2],
                                    [attachment1, attachment2])
        expected = [('report.1', 'name1', 'content1'),
                    ('report.2', 'name2', 'content2'),
                    ('attachment.1', 'attachment_name1', 'attachment_content1'),
                    ('attachment.2', 'attachment_name2', 'attachment_content2')]
        self.assertEquals(files, expected)

    def test_generate_form_data_2_xml_0_attachments(self):
        report1 = ("name1", "content1")
        report2 = ("name2", "content2")
        files = _generate_form_data([report1, report2])
        expected = [('report.1', 'name1', 'content1'),
                    ('report.2', 'name2', 'content2')]


    def test_generate_form_data_0_xml_2_attachments(self):
        attachment1 = ("attachment_name1", "attachment_content1")
        attachment2 = ("attachment_name2", "attachment_content2")
        # result xmls are mandatory for the interface so an exception should be
        # raised
        self.assertRaises(ValueError,
                          _generate_form_data,
                          [],
                          [attachment1,
                           attachment2])


if __name__ == '__main__':
    unittest.main()
