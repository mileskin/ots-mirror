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

"""
The EmailPlugin assumes an smtp server is set up 

This test checks the high level functions of the Plugin
and server are behaving

i.e. That a `publish` sends an email correctly 

This test uses a gmail account linking
to the api provided by  

https://github.com/drewbuschhorn/gmail_imap

to access the email. 
"""

import unittest
import getpass
import time
from random import Random
from ots.common.dto.api import OTSException, Packages, Results, Monitor

from ots.common.dto.api import Packages
from ots.plugin.email.api import EmailPlugin
    
#FIXME Add your test email recipient here

RECIPIENT = "foo@bar.com"

def pop_inbox():
    """
    rtype : C{tuple} of C{str}, C{float}
    rparam : The subject and the time
    """
    #This assumes a gmail recipient
    #Override this method with your preferred 
    #test recipient as required
    from gmail_imap import gmail_imap
    user = RECIPIENT
    password = getpass.getpass()
    gmail = gmail_imap.gmail_imap(user, password)
    gmail.mailboxes.load()
    gmail.messages.process("INBOX")
    message = gmail.messages[-1]
    gmail.logout()
    return message.Subject
    
class TestEmailPlugin(unittest.TestCase):

    def test_publish(self):
        
        rnd = Random()
        reqnumber = rnd.randint(100, 1000)
        
        email_plugin = EmailPlugin(reqnumber, 2222, 
                                   "sw_product", 
                                   "www.meego.com",
                                   email = "on",
                                   email_attachments = "on",
                                   notify_list=[RECIPIENT],
                                   build_url="build_url %s")
        exc = OTSException()
        exc.strerror = "foo"
        results_1 = Results("foo", "<foo>foo</foo>", 
                            environment = "foo")
        results_2 = Results("bar", "<bar>bar</bar>",
                            environment = "bar")
        results_list = [results_1, results_2]
        email_plugin.set_exception(exc)
        email_plugin.set_expected_packages(Packages("env", ["foo", "bar", "baz"]))
        email_plugin.set_tested_packages(Packages("env", ["foo", "bar", "baz"]))
        email_plugin.set_results(results_list)
        email_plugin.add_monitor_event(Monitor())
        email_plugin.set_testrun_result("PASS")
        email_plugin.publish()
        time.sleep(2)
        header = pop_inbox()
        expected = "[OTS] [sw_product] Req#" + str(reqnumber) +": PASS"
        self.assertTrue(expected, header)

if __name__ == "__main__":
    unittest.main()
