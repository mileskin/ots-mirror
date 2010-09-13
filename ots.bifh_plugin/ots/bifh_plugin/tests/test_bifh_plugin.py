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

import socket
import datetime

from ots.bifh_plugin.bifh_plugin import BifhPlugin

class BifhMock(object):
    def __init__(self):
        self.text = None
        self.url = None
        self.request_id = None

    def get_urls(self, request_id):
        urls = dict()
        urls["url"] = "old_url"
        urls["text"] = "text"
        return (urls,)

    def results(self, request_id):
        result = dict()
        dummypackage = dict()
        dummypackage['binary_name'] = "dummypackage"
        result['packages'] = [dummypackage]
        return result

    def add_url(self, request_id, text, url):
        if text == "timeout":
            raise socket.timeout
        self.text = text
        self.request_id = request_id
        self.url = url

    def add_attachment(self,
                       request_id,
                       label,
                       filename,
                       description,
                       content):
        self.request_id = request_id
        self.label = label
        self.filename = filename
        self.description = description
        self.content = content


MOCK = BifhMock()

def get_xmlrpc_mock():
    mock = BifhMock()
    mock.bifh = BifhMock()
    mock.bifh.users = BifhMock()
    mock.bifh.users.request = MOCK
    return mock


class TestBifhPlugin(unittest.TestCase):


    def setUp(self):
        self.plugin = BifhPlugin(None, 666)
        self.plugin._create_proxy = get_xmlrpc_mock

    def tearDown(self):
        pass

    def test_store_url(self):
        url = "http://something"
        text = "text"
        self.plugin.store_url(url, text)
        self.assertEquals(MOCK.url, url)
        self.assertEquals(MOCK.text, text)
        self.assertEquals(MOCK.request_id, 666)

    def _test_dont_store_if_old_url(self):
        url = "old_url"
        text = "text"
        self.plugin.store_url(url, text)
        self.assertEquals(MOCK.url, None)
        self.assertEquals(MOCK.text, None)
        self.assertEquals(MOCK.request_id, None)

    def test_get_target_packages(self):
        pkgs = self.plugin.get_target_packages("555")
        self.assertTrue(pkgs)

    def test_store_file(self):
        file_content = "content"
        filename = "name"
        label = "label"
        description = "description"
        self.plugin.store_file(file_content, filename, label, description)
        self.assertEquals(MOCK.request_id, 666)
        self.assertEquals(MOCK.filename, filename)
        self.assertEquals(MOCK.label, label)
        self.assertEquals(MOCK.description, description)

    def _test_timeout_handling(self):
        url = "http://something"
        text = "timeout" #causes mock to raise socket.Timeout
        self.assertEquals(self.plugin.store_url(url, text), None)

if __name__ == '__main__':
    unittest.main()
