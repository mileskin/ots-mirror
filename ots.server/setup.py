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

import sys
import os.path

from setuptools import setup, find_packages
from get_spec_version import get_spec_version

# In case of virtualenv install configuration files under virtual environment
if sys.prefix.startswith("/usr") or sys.prefix == "/":
    DATA_PREFIX = "/"
else:
    DATA_PREFIX = sys.prefix

setup(
      name="ots.server",
      author="meego-qa@lists.meego.com",
      version=get_spec_version(),
      include_package_data=True,
      namespace_packages=["ots"],
      packages=find_packages(),
      install_requires=['ots.results'],
      entry_points={"console_scripts":
                    ["ots_server = ots.server.xmlrpc.server:main", ]
                   },
      zip_safe=False,
      test_suite='ots.server.tests.suite',
      data_files=[(os.path.join(DATA_PREFIX, 'etc/ots/'),
                  ['ots/server/server.conf'])]
    )
