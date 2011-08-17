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
Scrapes the testrun logs
"""

import urllib2

from configuration import CONFIG
from BeautifulSoup import BeautifulSoup

def has_errors(testrun_id):
    """
    Checks if testrun has any error messages
    """
    log_url = CONFIG["global_log"]
    ret_val = False
    file =  urllib2.urlopen(log_url + "testrun/%s/" % testrun_id)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            try:
                error = td[4].findAll("span")[0].string
                if error == "ERROR":
                    ret_val = True
                    break
            except IndexError:
                pass

    return ret_val


def get_latest_testrun_id(log_url):
    """
    Scrape the latest testrun id from the global log
    """
    proxy_support = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    file =  urllib2.urlopen(log_url)
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    row1 = table.findAll("tr")[1]
    td = row1.findAll("td")[0]
    a = td.findAll("a")[0].string
    return a

def get_second_latest_testrun_id(log_url):
    """
    Scrape the second latest testrun id from the global log
    """
    latest = get_latest_testrun_id(log_url)
    file =  urllib2.urlopen(log_url)
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for row in rows:
        if row.findAll("td"):
            td = row.findAll("td")[0]
            a = td.findAll("a")[0].string
            if a != latest:
                return a
    return None

def has_message(testrun_id, string, times=None):
    """
    Tries to find a message in the log for the given testrun.
    Returns True if message was found.
    If times parameter given returns True if string is found as many times
    as defined by count.
    """
    log_url = CONFIG["global_log"]
    ret_val = False
    count = 0
    file =  urllib2.urlopen(log_url + "testrun/%s/" % testrun_id)
    soup = BeautifulSoup(file.read(),
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            if td[5].string and td[5].string.count(string):
                if times == None:
                    ret_val = True
                    break
                else:
                    count += 1
            elif td[5].string == None: # Check also <pre> messages </pre>
                if td[5].findAll("pre")[0].string.count(string):
                    if times == None:
                        ret_val = True
                        break
                    else:
                        count += 1
    
    if times == None:
        return ret_val
    else:
        if times == count:
            return True
        else:
            return False

if __name__ == "__main__":
    unittest.main()
