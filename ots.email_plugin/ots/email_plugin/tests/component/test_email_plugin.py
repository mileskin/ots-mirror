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

import StringIO

from ots.common.dto.api import Packages
from ots.email_plugin.api import EmailPlugin
    
RECIPIENT = "galvin.tom@gmail.com"

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
    gmail = gmail_imap(user, password)
    gmail.mailboxes.load()
    gmail.messages.process("INBOX")
    message = gmail.messages[-1]
    print message.date
    t = time.strptime(message.date, "%a, %d %b %Y %H:%M:%S +0000 (%Z)")
    gmail.logout()
    return message.Subject, t
    
class TestEmailPlugin(unittest.TestCase):

    def test_publish(self):
        email_plugin = EmailPlugin(111, 2222, "sw_product", "www.meego.com",
                                   notify_list = [RECIPIENT])
        email_plugin.set_all_publisher_uris({"foo" : "foo"})
        email_plugin.set_testrun_result(True)
        s_io = StringIO.StringIO()
        s_io.write("Hello World")
        email_plugin.set_results([s_io, s_io])
        packages = Packages("unittest", ["foo", "bar", "baz"])
        email_plugin.set_tested_packages(packages)
        t_before = time.gmtime()
        email_plugin.publish()
        time.sleep(2)
        t_after = time.gmtime()
        header, msg_t = pop_inbox()
        self.assertTrue(t_before <= msg_t <= t_after)
        expected = "[OTS] [sw_product] Req#111: True"
        self.assertTrue(expected, subject)

if __name__ == "__main__":
    unittest.main()
