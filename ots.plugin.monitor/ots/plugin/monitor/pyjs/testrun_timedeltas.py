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

"""
This is pyjamas code that gets compiled to javascript

See http://pyjs.org/controls_tutorial.html
"""

DEBUG = True

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.HTML import HTML

from pyjamas.chart.HovertextChunk import formatAsHovertext
from pyjamas.chart.GChart import GChart
from pyjamas.chart import AnnotationLocation
from pyjamas.chart import SymbolType
from pyjamas.ui.Button import Button

from pyjamas.JSONService import JSONProxy
from pyjamas.JSONParser import JSONParser

from pyjamas import Window

################################
# TestrunTimeDeltas
################################

class TestrunTimeDeltas(GChart):
    """
    Draws a stacked bar chart of the time deltas 
    for a testrun

    The central datastructure for the testrun_dts is:-

    @rtype: A list of [C{tuple} of (C{str}, 
                         [C{list} of 
                            [C{list} of C{float}]])]
    @rparam: A tuple of the testrun_id and the time deltas
                  for all the steps in the testrun 
    """

    COLORS = ['#a5cee3', '#1f78b3', '#b2de89',
              '#fcbf6f','#fb9a99', '#693d9a']

    STATE_COLORS = {None : '#FFFFFF',
                    '0' : '#FFA500',
                    '1' : '#FFA500', 
                    '2' : '#008000', 
                    '3' : '#FF0000', 
                    '4' : '#FF0000'}
        
    WIDTH = 600
    SIZE = 220
    MARGIN = 7
    MAX_X_LABEL_LENGTH = 6
    CHUNK_SIZE = 20
    BAR_WIDTH = 15
    Y_AXIS_SCALING = [1, 2, 3, 5, 7]
        
    def __init__(self):
        GChart.__init__(self)
        self.first = True
        self._steps = None
        self._end_step = None
        self._testrun_states = None
        self._timedeltas = None
        self._no_of_runs = None
        DEVICE_GROUP = None # Fixme
        self.remote = DataService()
        self.remote.get_total_no_of_testruns(DEVICE_GROUP, self)
        self.remote.get_event_sequence(self)
        #
        self.backButton = Button("<b><<</b>")
        self.backButton.addClickListener(self.onBack)

        self.forwardButton = Button("<b>>></b>")
        self.forwardButton.addClickListener(self.onForward)
        self.setChartFootnotes("")
      
    ##############################
    # SCALING
    ##############################

    def _get_longest_time(self, testrun_dts):
        """
        @type: See class docstring
        @param: The Testrun timedeltas for this `chunk`

        @rtype: C{int}
        @rparam: The longest time taken for this chunk of runs
        """
        longest_time = 0
        for testrun_idx in range(len(testrun_dts)):
            testrun_id, all_dts = testrun_dts[testrun_idx]
            testrun_time = sum([sum(step_dts) for step_dts in all_dts])
            longest_time = max(longest_time , testrun_time)
        return longest_time

    def _get_y_axis_size(self, longest_time):
        """
        Propose a size for the y axis

        @rtype: C{int}
        @rparam: The longest time taken for this chunk of runs
        """
        #FIXME: This is crude and ugly 
        #no doubt gchart provides something better natively
        candidate = 1
        for p in range(4):
            for scale in self.Y_AXIS_SCALING:
                candidate = scale*pow(10,p)
                if  candidate > longest_time:
                    break
        return candidate 
                
    ##############################
    # CHART RENDERING
    ##############################

    def _vertical_label(self, label, color):
        """
        The label rendered as vertical html

        @type label: C{str}
        @rparam label: The x axis label
        
        @rtype: C{str}
        @rparam: Html truncated vertical label
        """
        txt = '<html><center style="background-color:%s">'%(color)        
        label_len = min(len(label), MAX_X_LABEL_LENGTH)
        for idx in range(label_len):
            txt += "%s<br>"%(label[idx])
        txt += "</center></html>"
        return txt

    def _draw_bar_segment(self, testrun_id, curve, x_pos, step_idx, dts):
        """
        Draws one of the stacked bars

        @type testrun_id: C{str}
        @param testrun_id: The testrun id


        @type curve: L{pyjamas.chart.Curve}
        @param curve: The bar segment is a curve
        
        @type x_pos: C{int}
        @param x_pos: The position of the segment

        @type step_idx: C{int}
        @param step_idx: The index of the `step` in te testrun (for this bar)
        
        @type dts: C{list} of C{int}
        @param dts: The timedeltas for the whole testrun
        """
        symbol = curve.getSymbol()
        symbol.setSymbolType(SymbolType.BOX_NORTHEAST)
        symbol.setModelHeight(dts[step_idx])
        col = self.COLORS[step_idx]
        symbol.setBackgroundColor(col)
        symbol.setBorderColor(col)
        symbol.setWidth(self.BAR_WIDTH)
        start_time = sum(dts[:step_idx])
        curve.addPoint(x_pos, start_time)
        self._bar_segment_hover_text(testrun_id, symbol, step_idx, dts)

    def _bar_segment_hover_text(self, testrun_id, symbol, step_idx, dts):
        """
        The hover text for the bar segment
        @type testrun_id: C{str}
        @param testrun_id: The testrun id

        @type symbol: L{pyjamas.chart.Symbol}
        @param symbol: The
      
        @type step_idx: C{int}
        @param step_idx: The index of the `step` in te testrun (for this bar)
        
        @type dts: C{list} of C{int}
        @param dts: The timedeltas for the whole testrun
        """
        symbol.setHoverAnnotationSymbolType(
                                  SymbolType.ANCHOR_MOUSE_SNAP_TO_Y)
        symbol.setHoverLocation(AnnotationLocation.SOUTHEAST)
        start_time = sum(dts[:step_idx])
        end_time = sum(dts[:step_idx+1])
        step = self._steps[step_idx]
        ht = "<b>%s</b> <i>%s</i>: %ss-%ss" % (testrun_id, step, 
                                                start_time, end_time)
        ht = formatAsHovertext(ht)
        symbol.setHovertextTemplate(ht)

    def _render_axes(self, testrun_dts):
        """
        Render the stacked bars

        @type: See class docstring
        @param: The Testrun timedeltas for this `chunk`
        """
        x_axis = self.getXAxis()
        x_axis.clearTicks()
        x_axis.setTickThickness(0)
        x_axis.setAxisMin(0)
        x_axis.setAxisMax(self.SIZE)
        x_axis.addTick(0, self.backButton)
        x_axis.addTick(self.SIZE, self.forwardButton)
        #
        y_axis = self.getYAxis()
        y_axis.clearTicks()
        y_axis.setAxisMin(0)
        longest_time = self._get_longest_time(testrun_dts)
        y_max = self._get_y_axis_size(longest_time)
        y_axis.setAxisMax(y_max)  
        #FIXME 
        y_axis.addTick(y_max, "         %s"%(str(y_max)))
        y_axis.addTick(y_max / 2,  "         %s"%str(y_max/2))
      
    def _render_bars(self, testrun_dts):
        """
        Render the stacked bars

        @type: See class docstring
        @param: The Testrun timedeltas for this `chunk`
        """
        curve_idx = 0
        for testrun_idx in range(len(testrun_dts)):
            testrun_id, all_dts = testrun_dts[testrun_idx]
            #FIXME: Iterations in testrun steps need rendering
            dts = [sum(step_dts) for step_dts in all_dts]
            x_pos = self._bar_x_pos(testrun_idx) 
            for step_idx in range(len(dts)):
                dt = dts[step_idx]
                curve = self._get_curve(curve_idx)
                self._draw_bar_segment(testrun_id, curve, x_pos, step_idx, dts)
                if step_idx == 0:
                    self._x_labels(testrun_idx, testrun_id)  
                curve_idx += 1

    def _render_legend(self):
        """
        Render the legend
        """
        no_of_steps = len(self._steps)
        for step_idx in range(no_of_steps):
            curve = self.getCurve(step_idx) 
            curve.setLegendLabel(self._steps[step_idx])            

    def _x_labels(self, bar_idx, testrun_id):
        """
        Add the labels to the X Axis

        @type bar_idx: C{int}
        @param bar_idx: The index of the bar

        @type testrun_id: C{str}
        @param testrun_id: The testrun id for the label
        """
        state = self._testrun_states[bar_idx]
        color = self.STATE_COLORS[state]
        txt = self._vertical_label(str(testrun_id), color)
        x_pos = self._label_x_pos(bar_idx)
        self.getXAxis().addTick(x_pos + 2, txt)

    def _bar_x_pos(self, bar_idx):
        """
        The position on the X Axis of the bar

        @type bar_idx: C{int}
        @param bar_idx: The index of the bar

        @rtype: C{float}
        @rparam: The position of the bar
        """
        x_pos = ((bar_idx/20.) * (self.SIZE - self.MARGIN)) + self.MARGIN
        return x_pos

    def _label_x_pos(self, bar_idx):
        """
        The position on the X Axis of the bar

        @type bar_idx: C{int}
        @param bar_idx: The index of the bar

        @rtype: C{float}
        @rparam: The position of the bar
        """
        return self._bar_x_pos(bar_idx) + 1

    def _get_curve(self, curve_idx):
        """
        If a curve doesn't exist for the index it creates one 
        otherwise it replaces the existing curve

        @type curve_idx: C{int}
        @param curve_idx: The index of the curve

        @rtype: L{pyjamas.chart.Curve}
        @rparam: The curve
        """
        try:
            curve = self.getCurve(curve_idx)
            curve.clearPoints()
            curve.invalidate()
        except:
            self.addCurve()
            curve = self.getCurve()
        return curve

    def _render(self, testrun_dts):
        """
        Render a stacked barchart for the data

        @type: See class docstring
        @param: The Testrun timedeltas for this `chunk`
        """
        self.setChartTitle("<b>Testruns</b>")
        self.setChartSize(self.WIDTH, self.SIZE)
        self._render_axes(testrun_dts)
        self._render_bars(testrun_dts)
        self._render_legend()
        
    ###################################
    # HANDLERS
    ###################################

    def onRemoteError(self, code, message, request_info):
        RootPanel().add(HTML(message))
        if DEBUG:
            RootPanel().add(HTML(message))
        else: 
            Window.alert("Remote Error.")

    def onRemoteResponse(self, response, request_info):
        """
        Handler for the json HttpResponse
        """
        method_name, args = response
        if method_name == 'get_event_sequence':
            self._on_get_event_sequence(args)
        elif method_name == 'get_timedeltas':
            self._on_get_timedeltas(args)
        elif method_name == 'get_total_no_of_testruns':
            self._on_get_total_no_of_testruns(args)
        elif method_name == 'get_testrun_states':
            self._on_get_testrun_states(args)

    def _on_get_timedeltas(self, timedeltas):
        """
        Handler for `get_timedeltas`

        @type: See class docstring
        @param: The Testrun timedeltas for this `chunk`
        """
        testrun_ids = [testrun_id for testrun_id, dts in timedeltas]
        self.remote.get_testrun_states(testrun_ids, self)
        self._timedeltas = timedeltas
               
    def _on_get_event_sequence(self, event_sequence):
        """
        Handler for `get_event_sequence`

        @type: C{list} of C{str}
        @param: The sequence of events corresponding to the timedeltas
        """
        if self._steps is None:
            self._steps = []
            for idx in range(1, len(event_sequence)):
                step = "%s->%s"%(event_sequence[idx-1],
                                 event_sequence[idx])
                self._steps.append(step)

    def _on_get_total_no_of_testruns(self, no_of_runs):
        """
        Handler for `get_total_no_of_testruns`

        @type: C{int}
        @param: The total no of runs that have been monitored 
                for the device group selection
        """
        self._no_of_runs = no_of_runs
        self._end_step = no_of_runs
        self.remote.get_timedeltas(self._end_step - self.CHUNK_SIZE, 
                                   self._end_step, 
                                   -1,
                                   DEVICE_GROUP, self)
    
    def _on_get_testrun_states(self, states):
        """
        Handler for `get_testrun_states`

        @type: C{list} of C{str}
        @param: The states of the queried testruns
        """
        self._testrun_states = states
        self._render(self._timedeltas)
        self.update()
        
    def onForward(self):
        """
        Forward Click handler
        """
        start = self._end_step - (2 * self.CHUNK_SIZE)
        start = max(0, start)
        end = start + self.CHUNK_SIZE
        self.remote.get_timedeltas(start, end, -1, None, self)
        self._end_step = end

    def onBack(self):
        """
        Back Click handler
        """
        end = self._end_step + (2 * self.CHUNK_SIZE)
        end = min(end, self._no_of_runs)
        start = end - self.CHUNK_SIZE
        self.remote.get_timedeltas(start, end, -1, None, self)
        self._end_step = end


##############################
# DataService
##############################
                     
class DataService(JSONProxy):
    methods = ['get_timedeltas', 
               'get_event_sequence',
               'get_total_no_of_testruns',
               'get_testrun_states']

    #TODO: Add your root URL here
    ROOT_URL = 'http://127.0.0.1/services/'
    
    def __init__(self):
        if DEBUG == True :
            services = 'services/'
        else: 
            services = self.ROOT_URL
        JSONProxy.__init__(self, services, 
                           DataService.methods)
