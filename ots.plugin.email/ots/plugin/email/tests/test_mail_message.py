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
import StringIO

from email.mime.multipart import MIMEMultipart

from ots.common.dto.api import OTSException, Packages, Results

from ots.plugin.email.templates import DEFAULT_MESSAGE_BODY
from ots.plugin.email.templates import DEFAULT_MESSAGE_SUBJECT

from ots.plugin.email.mail_message import format_result
from ots.plugin.email.mail_message import format_source_uris
from ots.plugin.email.mail_message import format_packages
from ots.plugin.email.mail_message import MailMessage

BODY = 'SW Product     : sw_product\nBuild ID: request_id\nOTS testrun ID: testrun_uuid\n\nTest packages:\n  env:  baz foo bar\n\nTest result: PASS\n\nTest result details:\n\nmeego: www.meego.com\nnokia: www.nokia.com\nintel: www.intel.com\n\nBuild request:\nbuild_url request_id\n'

SUBJECT = "[OTS] [sw_product] Req#request_id: PASS"

class TestMailMessage(unittest.TestCase):

    def test_format_result(self):
        self.assertEquals("PASS", format_result("PASS", None))
        self.assertEquals("FAIL", format_result("FAIL", None))
        exc = OTSException()
        exc.strerror = "foo"
        self.assertEquals("FAIL (Error: foo, Error code:  )", format_result("FAIL", exc))
        

    def test_format_source_uris(self):
        source_uris = {"meego" : "www.meego.com",
                       "intel" : "www.intel.com",
                       "nokia" : "www.nokia.com"}
        expected = 'meego: www.meego.com\nnokia: www.nokia.com\nintel: www.intel.com'
        self.assertEquals(expected, format_source_uris(source_uris))

    def test_format_packages(self):
        packages = Packages("env", ["foo", "bar", "baz", "undefined"])
        self.assertEquals("  env:  baz foo bar\n",
                          format_packages(packages))
        self.assertEquals("(none)\n", 
                          format_packages(None))


    def test_init(self):
        mail_message = MailMessage("me@me.com", "message", "subject")
        mail_message.message_template = "message"
        mail_message.subject_template = "subject"
        mail_message = MailMessage("me@me.com")
        self.assertEquals(DEFAULT_MESSAGE_SUBJECT,
                          mail_message.subject_template)
        self.assertEquals(DEFAULT_MESSAGE_BODY,
                          mail_message.message_template)

    def test_body(self):
        mail_message = MailMessage("me@me.com")
        source_uris = {"meego" : "www.meego.com",
                       "intel" : "www.intel.com",
                       "nokia" : "www.nokia.com"}
        
        body = mail_message._body("request_id", "testrun_uuid", "sw_product",
                                  "PASS", None, 
                                  Packages("env", ["foo", "bar", "baz"]),
                                  source_uris, "build_url %s")
        self.assertEquals(BODY, body) 
                      
    def test_subject(self):
        mail_message = MailMessage("me@me.com")
        subject = mail_message._subject("request_id", "sw_product", "PASS")
        self.assertEquals(SUBJECT, subject)

    def test_message(self):
        mail_message = MailMessage("me@me.com")
        results_1 = Results("foo", "<foo>foo</foo>", 
                            environment = "foo")
        results_2 = Results("bar", "<bar>bar</bar>",
                            environment = "bar")
        results_list = [results_1, results_2]
        source_uris = {"meego" : "www.meego.com",
                       "intel" : "www.intel.com",
                       "nokia" : "www.nokia.com"}

        message = mail_message.message("request_id", "testrun_uuid", 
                                       "sw_product",
                                       "PASS", results_list, None,
                                       Packages("env", ["foo", "bar", "baz"]),
                                       source_uris,
                                       ["you@you.com"], 
                                       True,  
                                       "build_url %s")
        self.assertTrue(isinstance(message, MIMEMultipart))
    
if __name__ == "__main__":
    import logging
    logging.basicConfig()
    unittest.main()
