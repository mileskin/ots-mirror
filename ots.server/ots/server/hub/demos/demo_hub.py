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
High level demo of the hub

You need to run up the worker in another terminal:

$cd $WORKER
$python worker.py -c ./config.ini
"""

#FIXME: A WIP. This needs building on and working into 
#automated system tests 

import logging

from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.hub.api import Hub

options_dict = {"image" : "www.nokia.com" ,
                "rootstrap" : "www.meego.com",
                "packages" : "hw_pkg1-test pkg2-test pkg3-test",
                "plan" : "111",
                "execute" : "true",
                "gate" : "foo",
                "label": "bar",
                "hosttest" : "host_pkg1-test host_pkg2-test host_pkg3-test",
                "device" : "baz",
                "emmc" : "",
                "distribution-model" : "",
                "flasher" : "",
                "testfilter" : "",
                "input_plugin" : "bifh",
                "email" : "on",
                "email-attachments" : "on"}

def demo():
    """
    A rough and ready demo
    """
    taskrunner = taskrunner_factory("foo", 2, 1)
    taskrunner.add_task(["sleep", "1"])
    taskrunner.add_task(["echo", "hello world"])

    hub = Hub("example_sw_product", 1111,  **options_dict)
    hub._taskrunner = taskrunner
    hub.run()

if __name__ == "__main__":
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    demo()
