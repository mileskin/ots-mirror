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
import re

from configuration import CONFIG
from BeautifulSoup import BeautifulSoup
from custom_exceptions import SystemTestException

def testrun_log_urls(testrun_ids):
    return map(testrun_log_url, testrun_ids)

def testrun_log_url(testrun_id):
    return "%s/testrun/%s/" % (global_log_url(), testrun_id)

def global_log_url():
    return "http://" + CONFIG["server"] + "/logger/view"

def log_page_contains_errors(testrun_id):
    """
    Checks if testrun has any error messages
    """
    ret_val = False
    soup = _load_testrun_log_page(testrun_id)
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


def log_page_contains_message(testrun_id, original_string, times=None):
    """
    Tries to find a message in the log for the given testrun.
    Returns True if message was found.
    If times parameter given returns True if string is found as many times
    as defined by count.
    """
    string = _replace_keywords(original_string, testrun_id)
    ret_val = False
    count = 0
    soup = _load_testrun_log_page(testrun_id)
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

def log_page_contains_regexp_pattern(testrun_id, original_string, pattern):
    """
    Tries to match a regular expression with a message in the log for
    the given testrun. Returns True if a matching message was found.
    """
    pattern_to_search = re.compile(pattern)

    string = _replace_keywords(original_string, testrun_id)
    ret_val = False
    soup = _load_testrun_log_page(testrun_id)
    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            if td[5].string and pattern_to_search.search(td[5].string):
                ret_val = True
                break

            elif td[5].string == None and len(td[5].findAll("pre")) > 0 \
                and pattern_to_search.search(td[5].findAll("pre")[0].string):
                    ret_val = True
                    break
    return ret_val

def _replace_keywords(string, testrun_id):
    return string.replace("__TESTRUN_ID__", testrun_id)

def _load_testrun_log_page(testrun_id):
    url = global_log_url() + "/testrun/%s/" % testrun_id
    try:
        file = urllib2.urlopen(url)
    except Exception, e:
        raise SystemTestException("failed opening URL '%s'" % url, e)
    soup = BeautifulSoup(file.read(),
                         convertEntities=BeautifulSoup.ALL_ENTITIES)
    return soup


###############################################################################

if __name__ == "__main__":
    unittest.main()

