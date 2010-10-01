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
import datetime
from ots.server.input.resultsplugin import InputResultsPlugin    
from ots.common.interfaces.inputplugin import InputPlugin
from ots.common import resultobject


class testInputResultsPlugin(unittest.TestCase):
    
    def setUp(self):

        self.input_plugin = Input_plugin_mock()
        self.plugin = InputResultsPlugin(self.input_plugin)
            
    def tearDown(self):
        pass

        
    def test_store_result_file(self):

        result = resultobject.ResultObject(name="resultfile",
                                             content="foo",
                                             environment="hardware")

        self.plugin.add_result_object(result)
        self.plugin.save_results(Testrun_mock())
        self.assertEquals(self.input_plugin.file_content, "foo")
        self.assertTrue(self.input_plugin.filename.endswith("-hardware-resultfile"))
        self.assertTrue(self.input_plugin.label.endswith("-hardware-resultfile"))



class Testrun_mock(object):
    def get_testrun_id(self):
        return "666"

    def get_request_id(self):
        return "666"
    def get_start_time(self):
        return datetime.datetime.now()

class Input_plugin_mock(InputPlugin):

    def __init__(self):
        self.url = None
        self.text = None
        self.file_content = None
        self.filename = None
        self.label = None
        self.description = None



    def store_url(self, url, text):
        self.url = url
        self.text = text

    def store_file(self,
                   file_content,
                   filename,
                   label,
                   description):

        self.file_content = file_content
        self.filename = filename
        self.label = label
        self.description = description



if __name__ == '__main__':
    unittest.main()
