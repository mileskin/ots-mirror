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

from ots.results.results_dispatcher_base import ResultsDispatcherBase

class TestResultsDispatcherBase(unittest.TestCase):
    
    def test_tag_method_name(self):
        name = ResultsDispatcherBase._method_name("foo")
        self.assertEquals("_foo", name)

    def test_dispatch(self):
        dispatcher = ResultsDispatcherBase()
        dispatcher.foo = lambda x, y: x + y
        self.assertEquals(3, dispatcher._dispatch("foo", 1, 2))

    def test_dispatch_element(self):
        class ElementStub:
            tag = "foo"
        dispatcher = ResultsDispatcherBase()
        dispatcher._foo = lambda x: "pre" + x.tag 
        self.assertEquals("prefoo" , dispatcher.dispatch_element(ElementStub()))

if __name__ == "__main__":
    unittest.main()
