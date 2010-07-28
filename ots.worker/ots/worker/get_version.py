# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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
import ots.worker
import re

def get_version():
    """
    Get the version from the PKG-INFO
    """
    version = None
    ots_worker_path = os.path.dirname(os.path.abspath(ots.worker.__file__))
    egg_path = os.path.split(os.path.split(ots_worker_path)[0])[0]
    pkg_info_path = os.path.join(egg_path, "EGG-INFO", "PKG-INFO")
    if not os.path.exists(pkg_info_path):
        #So we have a developer egg
        pkg_info_path = os.path.join(egg_path,"ots.worker.egg-info", "PKG-INFO")
    if os.path.exists(pkg_info_path):
        pkg_info = open(pkg_info_path, "r")
        for line in pkg_info.readlines():
            if re.search("\AVersion:", line):
                version = line.split(":")[1].strip()
                break
    return version 

if __name__ == "__main__":
    print get_version()
