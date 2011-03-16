#!/usr/bin/python
# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

""" Gets version number from the spec file """

import os

def get_spec_version():
    spec_location = "python-ots.spec"
    try:
        if not os.path.exists(spec_location):
            spec_location = "../" + spec_location
        specfile = open(spec_location)
        for line in specfile:
            version = line.find('Version:')
            if version == -1:
                continue
            version = line.split(":")[1].strip()
            break
        specfile.close()
        return version
    except:
        return None

if __name__ == "__main__":
    print get_spec_version()