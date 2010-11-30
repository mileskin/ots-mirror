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

def find_message(testrun_id, string):
    """
    Tries to find a message in the log for the given testrun
    Returns True if message was found
    """
    ret_val = False
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            # todo find instead of exact match
            if td[0].string == testrun_id and td[4].string == string:
                ret_val = True
                #print td[4].string
                break

    return ret_val

def has_errors(testrun_id):
    """
    Checks if testrun has any error messages
    """
    ret_val = False
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        error = ""
        td = tr.findAll("td")
        if td:

            if td[0].string == testrun_id:
                # Error has some styling:
                try:
                    error  =  td[3].findAll("div")[0].findAll("b")[0].string
                except IndexError:
                    pass
                if error == "ERROR":
                    ret_val = True
                    print error
                    #break
    return ret_val


if __name__ == "__main__":
    testrun_id = get_latest_testrun_id()
    string = "Result set to ERROR"
    find_message(testrun_id, string)
    print has_errors(testrun_id)
