# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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

import StringIO
from tempfile import mktemp
from zipfile import ZipFile

from ots.common.dto.api import Results, Environment

from ots.plugin.email.attachment import _zip_info
from ots.plugin.email.attachment import _zip_file
from ots.plugin.email.attachment import attachment

class TestAttachment(unittest.TestCase):

    def test_zip_info(self):
        info = _zip_info("env", "name")
        self.assertTrue(isinstance(info.date_time, tuple))
        self.assertTrue(28704768, info.external_attr)
        self.assertTrue(8, info.compress_type) 

    def test_zipped(self):
        results_1 = Results("foo", "<foo>foo</foo>", 
                            environment = "foo")
        results_2 = Results("bar", "<bar>bar</bar>",
                            environment = "bar")
        results_list = [results_1, results_2]
        file =  _zip_file("111", results_list)
        tmp_filename = mktemp()
        f = open(tmp_filename, "wb")
        f.write(file.read())
        f.close()
        z = ZipFile(tmp_filename)
        self.assertEquals(2, len(z.infolist()))
        contents = ''.join([z.read(name) for name in z.namelist()])
        expected = "<foo>foo</foo><bar>bar</bar>"
        self.assertEquals(expected, contents)

    def test_attachment(self):
        results_1 = Results("foo", "<foo>foo</foo>", 
                            environment = "foo")
        results_2 = Results("bar", "<bar>bar</bar>",
                            environment = "bar")
        results_list = [results_1, results_2]
        
        a = attachment(111111, results_list)
        self.assertEquals("OTS_testrun_111111.zip", a.get_filename())
        tmp_filename = mktemp()
        pl = a.get_payload(decode = True)
        f = open(tmp_filename, "wb")
        f.write(pl)
        f.close()
        z = ZipFile(tmp_filename)
        self.assertEquals(2, len(z.infolist()))
    
if __name__ == "__main__":
    unittest.main()
