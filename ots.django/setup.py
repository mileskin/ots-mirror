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

from setuptools import setup, find_packages
from get_spec_version import get_spec_version

setup(
      name="ots.django",
      author="teemu.vainio@ixonos.com",
      namespace_packages=["ots", "ots.django"],
      version=get_spec_version(),
      include_package_data=True,
      packages=find_packages(),      
      data_files=[('/usr/share/ots/django/logger', ['ots/django/logger/templates/ots.wsgi']),
                  ('/usr/share/ots/django/logger/media', ['ots/django/logger/templates/media/logo.png']),
                  ('/usr/share/ots/django/logger/styles', ['ots/django/logger/templates/styles/custom.css']),
                  ('/usr/share/ots/django/logger/logger', ['ots/django/logger/templates/logger/index.html',
                                                           'ots/django/logger/templates/logger/workers_view.html',
                                                           'ots/django/logger/templates/logger/filter_message_view.html',
                                                           'ots/django/logger/templates/logger/basic_testrun_view.html',
                                                           'ots/django/logger/templates/logger/advanced_message_view.html',
                                                           'ots/django/logger/templates/logger/logger_base.html',
                                                           'ots/django/logger/templates/logger/message_details_view.html',]),
                 ]
      )
