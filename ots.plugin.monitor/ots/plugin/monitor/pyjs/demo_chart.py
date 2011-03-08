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

import pyjd
pyjd.setup("./public/DemoChart.html")

from pyjamas import DeferredCommand
from pyjamas.ui.HTML import HTML
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.chart import GChart

from pyjamas.Canvas.GWTCanvas import GWTCanvas

from testrun_timedeltas import TestrunTimeDeltas

class AddOneChart:
    def __init__(self, gchart, needsUpdate=True):
        self.gchart = gchart
        self.needsUpdate = needsUpdate
    
    def execute(self):
        RootPanel("demochart").add(HTML("DEMO"))
        RootPanel("demochart").add(self.gchart)
        if self.needsUpdate:
            self.gchart.update()
        
def addChart(gchart):
    DeferredCommand.add(AddOneChart(gchart, True))

def addChartNoUpdate(gchart):
    DeferredCommand.add(AddOneChart(gchart, False))

class GWTCanvasBasedCanvasFactory(object):
    def create(self):
        return GWTCanvas()



def onModuleLoad():
   GChart.setCanvasFactory(GWTCanvasBasedCanvasFactory())
   addChart(TestrunTimeDeltas())
   RootPanel("loadingMessage").setVisible(False)
    
onModuleLoad()
pyjd.run()
