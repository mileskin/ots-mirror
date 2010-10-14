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

import os

import unittest

from ots.worker.worker import worker_factory

class TestWorker(unittest.TestCase):

    def test_config(self):
        dirname = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        config = os.path.join(dirname, "config.ini")
        worker = worker_factory(config)

        self.assertEquals("/", worker._vhost)
        self.assertEquals(5672, worker._port)
        self.assertEquals("guest", worker._username)
        self.assertEquals("guest", worker._password)
        self.assertEquals("foo", worker._devicegroup)

if __name__ == "__main__":
    unittest.main()
