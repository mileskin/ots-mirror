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

#WIP

import sys
import uuid

from PyQt4 import QtGui

from ots.common.framework.plugin_base import PluginBase 

class PublisherWidget(QtGui.QWidget):

    def __init__(self, parent, testrun_uuid):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle("Testrun: %s"%(testrun_uuid))
        print testrun_uuid
      
class PubPluginDemo(PluginBase):
    
    def __init__(self, request_id, testrun_uuid, sw_product, image, **kwargs):
        app = QtGui.QApplication(sys.argv)
        self.publisher_widget = PublisherWidget(None, testrun_uuid)
        self.publisher_widget.show()
        app.exec_()

    def set_results(self, results):
        print results
        

if __name__ == "__main__":
    PubPluginDemo(111, uuid.uuid1().hex, "demo", "www.meego.com")
