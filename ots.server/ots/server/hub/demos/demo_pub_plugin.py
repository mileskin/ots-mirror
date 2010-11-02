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

"""
A small demo to help Publisher Plugin Authors
integrate with OTS
"""

import sys
import uuid

from PyQt4 import QtGui
from PyQt4 import QtCore

from ots.server.hub.tests.component.mock_taskrunner import \
                                            MockTaskRunnerResultsPass
from ots.server.hub.hub import _run 


class DemoDialog(QtGui.QWidget):
    """
    Top Level Dialog
    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 350, 80)
        self.setWindowTitle('OTS Publisher Demo')

        self.button = QtGui.QPushButton('Run', self)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)

        self.button.move(20, 20)
        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.run)
        self.setFocus()
        
        self.line_edit = QtGui.QLineEdit(self)
        self.line_edit.move(130, 22)
    
    def run(self):
        run(self, text = self.line_edit.text())
       
def run(parent, text):
    """
    @type parent : C{QWidget}
    @param parent : The Parent Widget

    @type text : C{str}
    @param text : Demonstrate extension of API
    """
    mock_task_runner = MockTaskRunnerResultsPass()
    run_test = mock_task_runner.run
    testrun_uuid = uuid.uuid1().hex

    class OptionsStub():
        image =  "www.meego.com"
        is_package_distributed = False
        hw_packages = []
        host_packages = []
        emmc = "emmc"
        testfilter = None
        flasher = None
    options_stub = OptionsStub()
    _run("sw_product", "request_id", testrun_uuid, 
         ["a", "b", "c"], run_test, 
         options_stub, parent = parent, text = text)

def main():
    """
    Run a stubbed up Testrun
    within a small PyQt app 
    to show the use of the Publisher Plugin
    """
    app = QtGui.QApplication(sys.argv)
    demo_dlg = DemoDialog()
    demo_dlg.show()
    app.exec_()

if __name__ == "__main__":
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    main()
