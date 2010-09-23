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

import sys
from pickle import loads, dumps

from ots.common.ots_exception import OTSException

class MyException(OTSException):
    errno = 999
        

class TestOTSException(unittest.TestCase):
    
    def test_pickle1(self):
        exc = OTSException(111, "bar")
        p = dumps(exc)
        exc_loaded = loads(p)
        self.assertEquals(111, exc_loaded.errno)
        self.assertEquals("bar", exc_loaded.strerror)
        def raises():
            raise exc_loaded
        self.assertRaises(OTSException, raises)

    def test_pickle2(self):
        def raises():
            raise MyException
        try:
            raises()
        except:
            exc = sys.exc_info()[1]
            p = dumps(exc)
            exc_loaded = loads(p)
            self.assertEquals(999, exc_loaded.errno)
       
    def test_init(self):
        exc = OTSException()
        self.assertEquals('', exc.errno)
        self.assertEquals('', exc.strerror)
        exc = OTSException(1, "foo")
        self.assertEquals(1, exc.errno)
        self.assertEquals("foo", exc.strerror)

if __name__ == "__main__":
    unittest.main()
