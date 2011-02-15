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

import os.path; j = os.path.join
import sys
from setuptools import setup, find_packages
from get_spec_version import get_spec_version

if sys.prefix.startswith("/usr") or sys.prefix == "/":
    data_prefix="/" #install data and config files relative to root
else:
    data_prefix=sys.prefix #we are inside virtualenv, so install files relative to it


setup(
      name="ots.plugin.qareports",
      author="teemu.vainio@ixonos.com",
      namespace_packages=["ots", "ots.plugin", "ots.plugin.qareports"],
      version=get_spec_version(),
      include_package_data=True,
      packages=find_packages(),
      install_requires=['ots.server', 'configobj'],
      entry_points={"ots.publisher_plugin":
                    ["publisher_klass = "\
                     "ots.plugin.qareports.qareports_plugin:QAReportsPlugin"]},
                     data_files=[(j(data_prefix,'etc'),
                                  ['ots/plugin/qareports/ots_plugin_qareports.conf'])]
      )
