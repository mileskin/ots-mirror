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
OTS log based system tests.

These tests expect that you have full ots system set up. They trigger testruns
and check http logs for expected results

"""

import urllib2
from BeautifulSoup import BeautifulSoup
SERVER = "localhost"
URL = "http://%s/logger/view/ots/%s/"
GLOBAL_LOG = "http://%s/logger/view/" % (SERVER)

def get_latest_testrun_id():
    """
    Scrape the latest testrun id from the global log
    """
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    row1 = table.findAll("tr")[1]
    td = row1.findAll("td")[0].string
    return td

def scrape_log(testrun_id):
    """
    Check the web page of the Tero log for the given testrun_id
    and return the Result
    """
    ret_val = None
    file =  urllib2.urlopen("/%s/"%(CITA_SERVER, testrun_id))
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[0]
    rows = table.findAll("tr")
    for tr in rows:
        if "Result"in tr.findAll("th")[0]:
            td = tr.findAll("td")[0]    
            for str_result in ["ERROR", "PASS", "FAIL", "NOT IN DB."]:
                ret_val = td.find(text = str_result)
                if ret_val is not None:
                    break
    return ret_val
if __name__ == "__main__":
    print get_latest_testrun_id()
