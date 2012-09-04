# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# pinggraph - uses cairo to graph ping
# Copyright (c) 2012 Gavin Langdon <puttabutta@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#------------------------------------------------------------------------------


import cairo


PING_LIMIT = 240

class PingGraph(object):
  def __init__(self, dic, darea):
    self.darea = darea
    dic['on_ping_graph_draw'] = self.on_ping_graph_draw

    self.data = None

  def set_data(self, data):
    self.data = data

  def queue_draw(self):
    rect = self.darea.get_allocation()
    self.darea.queue_draw_area(0, 0, rect.width, rect.height)
    self.darea.set_visible(True)

  def on_ping_graph_draw(self, widget, cx):
    widget.set_visible(self.data != None)
    if not self.data:
      return

    rect = widget.get_allocation()
    
    cx.set_source_rgb(1.0,1.0,1.0)
    cx.paint()

    g = cairo.LinearGradient(0, 0, 0, rect.height)
    g.add_color_stop_rgb(0.3, 1.0, 0.2, 0.2)
    g.add_color_stop_rgb(0.6, 1.0, 1.0, 0.2)
    g.add_color_stop_rgb(1.0, 0.2, 1.0, 0.2)
    cx.set_source(g)


    x = 0
    for i in range(len(self.data)):
      x = i * rect.width / (PING_LIMIT - 1)

      # rescaling graph
      y = rect.height - (self.data[i] * rect.height / 275)

      cx.line_to(x, y)
      #g = cairo.LinearGradient(x - divs, 0, x, 0)

      #cprev = self.data[max(i-1, 0)] 
      #ccur = self.data[i]

      #g.add_color_stop_rgb(0.0, (25 + float(cprev)) / 150, (300 - float(cprev)) / 150, 0.0)
      #g.add_color_stop_rgb(1.0, (25 + float(ccur)) / 150, (300 - float(ccur)) / 150, 0.0)
      #cx.set_source(g)
      #cx.fill()
      #cx.move_to(x, y)
    cx.line_to(x, rect.height)
    cx.line_to(0, rect.height)
    cx.fill()


