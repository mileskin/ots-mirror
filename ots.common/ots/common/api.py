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


#Protocol

from ots.common.protocol import OTSProtocol, OTSMessageIO, OTSProtocol
from ots.common.protocol import PROTOCOL_VERSION

#Containers

from ots.common.resultobject import ResultObject
from ots.common.packages import ExpectedPackages, TestedPackages
#from ots.common.executed_package import ExecutedPackage
#from ots.common.package_results import PackageResults
#

from ots.common.testrun_queue_name import testrun_queue_name
