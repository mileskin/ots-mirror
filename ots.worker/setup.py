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
      name="ots.worker",
      author="teemu.vainio@ixonos.com",
      version=get_spec_version(),
      include_package_data=True,
      namespace_packages=['ots'],
      packages=find_packages(),
      zip_safe=False,
      entry_points={"console_scripts":
                    ["conductor = ots.worker.conductor.conductor:main",
                     "ots_worker = ots.worker.worker:main"]},
      data_files=[(os.path.join(DATA_PREFIX, 'etc'),
                   ['ots.ini', 'ots/worker/conductor/conductor.conf']),
                   (os.path.join(DATA_PREFIX, 'etc/init.d/'),
                    ['ots-worker']),
                   (os.path.join(DATA_PREFIX, 'etc/conductor'), [])]
      )
