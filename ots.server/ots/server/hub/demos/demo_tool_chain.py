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
High level demo of the full tool chain

You need to run up the worker in another terminal:

$cd $WORKER
$python worker.py -c ./config.ini

And have a device connected 
"""

import logging

from ots.common.routing.api import DEVICE_GROUP

from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.hub.api import Hub

options_dict = {"packages" : "testrunner-lite-tests",
                "device" : "%s:foo"%(DEVICE_GROUP)}

def demo(image):
    """
    A Demo that run the full tool chain downstream of the hub

    @type: C{str}
    @param: The image url
    """
    options_dict["image"] = image
    hub = Hub("example_sw_product", 1111,  **options_dict)
    hub.run()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print
        print "Usage:"
        print "python demo_tool_chain.py http://path/to/your_image.tar.gz" 
        sys.exit()
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    image = sys.argv[1]
    print
    print "Running tool chain demo with image:", image
    print
    demo(image)
