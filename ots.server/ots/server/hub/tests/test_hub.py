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

from ots.server.hub.options import IMAGE, ROOTSTRAP, PACKAGES, PLAN
from ots.server.hub.options import EXECUTE, GATE, LABEL, HOSTTEST
from ots.server.hub.options import DEVICE, EMMC, EMMCURL, DISTRIBUTION, FLASHER
from ots.server.hub.options import TESTFILTER, INPUT, EMAIL, EMAIL_ATTACHMENTS

from ots.server.hub.hub import run

import unittest

options_dict = {IMAGE : "www.nokia.com" ,
                ROOTSTRAP : "www.meego.com",
                PACKAGES : "hw_pkg1 pkg2 pkg3",
                PLAN : "111",
                EXECUTE : "true",
                GATE : "foo",
                LABEL: "bar",
                HOSTTEST : "host_pkg1 host_pkg2 host_pkg3",
                DEVICE : "baz",
                EMMC : "",
                EMMCURL : "",
                DISTRIBUTION : "",
                FLASHER : "",
                TESTFILTER : "",
                INPUT : "bifh",
                EMAIL : "on",
                EMAIL_ATTACHMENTS : "on"}

class TestHub(unittest.TestCase):

    def test_run(self):
        run("foo", "bar", "baz", **options_dict)

if __name__ == "__main__":
    unittest.main()
