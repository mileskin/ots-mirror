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

import sys
import uuid
import logging 

from PySide import QtGui

from ots.common.framework.publisher_plugin_base import PublisherPluginBase 

LOG = logging.getLogger(__name__)

class PublisherDialog(QtGui.QDialog):
    """
    Publishes results from a Testrun
    """

    def __init__(self, parent, testrun_uuid, text):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Testrun: %s"%(testrun_uuid))
        self.resize(500, 70)        
        layout = QtGui.QVBoxLayout(self)
        #
        self.text_label = QtGui.QLabel(self) 
        self.text_label.setText("User input: %s"%(text))
        layout.addWidget(self.text_label)
        #       
        self.uris_label = QtGui.QLabel(self) 
        layout.addWidget(self.uris_label)
        #
        self.result_label = QtGui.QLabel(self) 
        layout.addWidget(self.result_label)
        #
        self.filenames_label = QtGui.QLabel(self) 
        layout.addWidget(self.filenames_label)
        #
        spacer = QtGui.QSpacerItem(20,40,
                                   QtGui.QSizePolicy.Minimum,
                                   QtGui.QSizePolicy.Expanding)

        layout.addItem(spacer)
        
class PySidePublisher(PublisherPluginBase):
    """
    A small demonstration on how to create a
    Publisher Plugin for OTS 
    """
    
    def __init__(self, request_id, testrun_uuid, sw_product, image, 
                 parent = None, text = None,**kwargs):
        LOG.debug("Initialising PySidePublisher")
        LOG.debug("Parent: %s"%(parent))
        LOG.debug("Testrun UUID: %s"%(testrun_uuid))
        LOG.debug("Text: %s"%(text))
        LOG.debug("kwargs: %s"%(kwargs))
        self.publisher_dialog = PublisherDialog(parent, testrun_uuid, text)
        self.publisher_dialog.show()
       
    def set_testrun_result(self, result):
        result_text = "No Packages"
        if result is not None:
            if result:
                result_text = "Pass"
            else:
                result_text = "Fail"
        self.publisher_dialog.result_label.setText("Result: %s"%(result_text))

    def get_this_publisher_uris(self):
        return {id(self) : None}

    def set_all_publisher_uris(self, uris):
        self.publisher_dialog.uris_label.setText("URIs: %s"%(uris))

    def set_results(self, results):
        filenames = [result.data.name for result in results]
        filenames = ','.join(filenames)
        self.publisher_dialog.filenames_label.setText(filenames)

if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    publisher_dialog = PublisherDialog(None, 111, "hello world")
    publisher_dialog.show()
    publisher_dialog.result_label.setText("Result: Pass")
    publisher_dialog.uris_label.setText("URIs: www.meego.com")
    publisher_dialog.filenames_label.setText("quark, strangeness, charm")
    app.exec_()
