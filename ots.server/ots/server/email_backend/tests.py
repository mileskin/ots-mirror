#!/usr/bin/python
# -*- coding: utf-8 -*-
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


"""Tests for Email Backend"""

import unittest
from ots.server.email_backend import email_backend
from ots.server.email_backend import mailmessage

import smtplib
from ots.common import testrun
from ots.common.resultobject import ResultObject
import logging
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',)

log = logging.getLogger('resultsplugin')



LINK_URLS = dict()
LINK_URLS['buildURL'] = "https://dummybuildmachineurl/%s/"
LINK_URLS['resultURL1'] = "http://dummyurl2/%s"
LINK_URLS['logURL'] =  "http://dummyurl/%s/"
LINK_URLS['resultURL2'] = "anotherurl%s"


#
# Email settings
#
EMAIL_SETTINGS = dict()
EMAIL_SETTINGS['fromAddress'] = "no_reply@localhost"
EMAIL_SETTINGS['smtpServer'] = "localhost"
EMAIL_SETTINGS['message_body'] = None
EMAIL_SETTINGS['message_subject'] = None

RESULT_XML = "dummyfile"


class TestEmailBackend(unittest.TestCase):
    """
    Unit tests for email backend. Uses MailerStub as mailer.
    """

    def setUp(self):
        self.testrun = testrun.Testrun()
        self.testrun.set_request_id("12345")
        self.testrun.set_sw_product("MySwProduct")
        self.testrun.set_email_list(["test.address@nospam.com"])
        self.testrun.options['email-attachments'] = True
        self.mailer = MailerStub()
        self.backend = email_backend.EmailBackend(self.testrun, LINK_URLS, 
                                                  EMAIL_SETTINGS, self.mailer)

    def test_MailToOneAddressWithResultPass(self):
        self.testrun.set_result("PASS")
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_MailToOneAddressWithResultFail(self):
        self.testrun.set_result("FAIL")
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_MailToOneAddressWithResultError(self):
        self.testrun.set_result("ERROR")
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_MailToTwoAddresses(self):
        self.testrun.set_email_list(["test.address1@nospam.com", "test.address2@nospam.com"])
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_MailWithTestPackages(self):
        self.testrun.set_result("PASS")
        pkgs = dict()
        pkgs["hardware"] = ["mypkg1-tests", "mypkg2-tests"]
        pkgs["scratchbox"] = ["hispkg1-tests", "hispkg2-tests"]
        pkgs["host_hardware"] = ["herpkg1-tests", "herpkg2-tests"]
        self.testrun.set_all_executed_packages(pkgs)
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_process_raw_file(self):
        """Test for process_raw_file method."""
        self.assertEquals(len(self.backend.result_files), 0)

        result_object1 = ResultObject("filename.xml", "filecontent", testpackage="my-tests", origin="", environment="")
        self.backend.process_raw_file(result_object1, self.testrun)
        self.assertEquals(len(self.backend.result_files), 1)
        self.assertEquals(self.backend.result_files[0], result_object1)

        result_object2 = ResultObject("filename.xml", "filecontent", testpackage="my-tests", origin="", environment="")
        self.backend.process_raw_file(result_object2, self.testrun)
        self.assertEquals(len(self.backend.result_files), 2)
        self.assertEquals(self.backend.result_files[0], result_object1)
        self.assertEquals(self.backend.result_files[1], result_object2)

    def test_MailTo20Addresses(self):
        aList = []
        for i in range(1,21):
            aList.append("test.address%s@nospam.com" % i)
        self.testrun.set_email_list(aList)
        self.backend.send_mail()
        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)

    def test_interfacemethod_name_exists(self):
        self.assertTrue(str(self.backend.name) != "")

    def test_interfacemethod_SaveRawFiles_exists(self):
        self.backend.saveRawFiles(files=None)

    def test_neg_test_RequestIdNotSet(self): #no mail sent
        self.testrun.set_request_id("")
        self.backend.send_mail()
        self.assertFalse(self.mailer.sendmailcalled, "mailer tried to send mail anyway")

    def test_neg_test_AddressListEmpty(self): #no mail sent
        self.testrun.set_email_list([])
        self.backend.send_mail()
        self.assertFalse(self.mailer.sendmailcalled, "mailer tried to send mail anyway")

    def test_neg_test_AddressListWrongType(self): #no mail sent
        self.testrun.set_email_list(666) #integer is not a list
        self.backend.send_mail()
        self.assertFalse(self.mailer.sendmailcalled, "mailer tried to send mail anyway")

    def _sendmailGotProperMessage(self):
        return (self.mailer.sendmail_args[2].find("To:") >= 0) #we could do more checks


class TestEmailBackendWithResultObjects(unittest.TestCase):
    """
    Unit tests for email backend using MailerStub.
    """

    def test_mail_complete_with_three_attachments(self):
        self.testrun = testrun.Testrun()
        self.testrun.set_request_id("12345")
        self.testrun.set_sw_product("MySwProduct")
        self.testrun.set_email_list(["test.address@nospam.com"])
        self.testrun.set_result("PASS")
        self.testrun.options['email-attachments'] = True
        pkgs = dict()
        pkgs["hardware"] = ["mypkg1-tests", "mypkg2-tests"]
        pkgs["scratchbox"] = ["hispkg1-tests", "hispkg2-tests"]
        pkgs["host_hardware"] = ["herpkg1-tests", "herpkg2-tests"]
        self.testrun.set_all_executed_packages(pkgs)
        self.mailer = MailerStub()

        self.backend = email_backend.EmailBackend(self.testrun, LINK_URLS, EMAIL_SETTINGS, self.mailer)

        for i,env in [(1,"hardware"),(2,"scratchbox"),(3,"host_hardware")]:
            result_object = ResultObject("filename%s.xml" % i, 
                                          RESULT_XML, 
                                          testpackage = "my-tests", 
                                          origin = "myworker", 
                                          environment = env)
            self.backend.pre_process_xml_file(result_object, self.testrun)

        self.backend.send_mail()

        self.assertTrue(self.mailer.newcalled)
        self.assertTrue(self.mailer.sendmailcalled)
        self.assertTrue(self._sendmailGotProperMessage())
        self.assertTrue(self.mailer.quitcalled)
        #TODO: check that resultfiles are attached!

    def _sendmailGotProperMessage(self):
        return (self.mailer.sendmail_args[2].find("To:") >= 0) #we could do more checks


class Test_mailmessage(unittest.TestCase):
    """
    Unit tests for mailmessage module.
    """
    def setUp(self):
        self.testrun = testrun.Testrun()
        self.testrun.set_request_id("12345")
        self.testrun.set_sw_product("MySwProduct")
        self.testrun.options['email-attachments'] = True
        self.from_address = "from.address@nospam.com"
        self.to_address_list = ["to.address@nospam.com"]
        self.build_url = "%s"
        result_object = ResultObject("filename.xml", 
                                      RESULT_XML, 
                                      testpackage = "my-tests", 
                                      origin = "myworker", 
                                      environment = "hardware")

        self.result_files = [result_object]

    def test_constants(self):
        mailmessage.DEFAULT_MESSAGE_BODY % ('1','2','3','4','5','6','7')
        mailmessage.DEFAULT_MESSAGE_SUBJECT % ('1','2','3')

    def test__create_without_result_files(self):
        msg = mailmessage._create(self.testrun, self.from_address, 
                                  self.to_address_list, self.build_url, [])
        self.assertTrue(msg["Subject"])
        self.assertTrue(msg["From"])
        self.assertTrue(msg['To'])
        self.assertTrue(len(msg.get_payload()) > 0)
        self.assertTrue(msg.is_multipart())
        self.assert_(msg.as_string().find("application/zip") == -1 )

    def test__create_with_result_files(self):
        msg = mailmessage._create(self.testrun, self.from_address, 
                                  self.to_address_list, self.build_url, 
                                  self.result_files)
        self.assertTrue(msg["Subject"])
        self.assertTrue(msg["From"])
        self.assertTrue(msg['To'])
        self.assertTrue(msg.is_multipart())
        self.assert_(msg.as_string().find("application/zip") != -1 )

    def test__create_when_email_attachments_is_disabled(self):
        self.testrun.options['email-attachments'] = False
        msg = mailmessage._create(self.testrun, self.from_address, 
                                  self.to_address_list, self.build_url, 
                                  self.result_files)
        self.assertTrue(msg["Subject"])
        self.assertTrue(msg["From"])
        self.assertTrue(msg['To'])
        self.assertTrue(msg.is_multipart())
        self.assert_(msg.as_string().find("application/zip") == -1 )

    def test_attach_as_zip_file(self):
        unique_id = "1"
        msg = MIMEMultipart()
        mailmessage.attach_as_zip_file(msg, self.result_files, unique_id)
        self.assert_(msg.as_string().find("application/zip") != -1 )


class TestEmailBackendLogMailer(unittest.TestCase):
    """Unit tests for email backend using LogMailer"""

    def setUp(self):
        self.testrun = testrun.Testrun()
        self.testrun.set_request_id("12345")
        self.testrun.set_sw_product("MySwProduct")
        self.testrun.set_email_list(["test.address@nospam.com"])
        self.backend = email_backend.EmailBackend(self.testrun, LINK_URLS, 
                                              EMAIL_SETTINGS, mailer="LOG_ONLY")

    def testMailToOneAddressWithResultPass(self):
        self.testrun.set_result("PASS")
        self.backend.send_mail()

    def testMailToOneAddressWithResultError(self):
        self.testrun.set_result("ERROR")
        self.testrun.set_error_info("A special error.")
        self.backend.send_mail()

    def test_MailWithTestPackages(self): #duplicate test. This allows evaluating the looks of mail message on screen
        self.testrun.set_result("PASS")
        pkgs = dict()
        pkgs["hardware"] = ["mypkg1-tests", "mypkg2-tests"]
        pkgs["scratchbox"] = ["hispkg1-tests", "hispkg2-tests"]
        pkgs["host_hardware"] = ["herpkg1-tests", "herpkg2-tests"]
        self.testrun.set_all_executed_packages(pkgs)
        self.backend.send_mail()


class MailerStub():
    """Stub which does not communicate with network or any server"""
    def __init__(self):
        self._smtp_server = ""
        self.newcalled = False
        self.sendmailcalled = False
        self.quitcalled = False
        self.sendmail_args = []
    def get_smtp_server(self):
        return self._smtp_server
    def new(self):
        self.newcalled = True
    def sendmail(self, from_address, to_address_list, message):
        self.sendmailcalled = True
        self.sendmail_args = [from_address, to_address_list, message]
        return None  #no failed addresses
    def quit(self):
        self.quitcalled = True


if __name__ == '__main__':
    unittest.main()

