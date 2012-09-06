# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# pinggraph - uses cairo to graph ping
# Copyright (c) 2012 Gavin Langdon <puttabutta@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#------------------------------------------------------------------------------

import cairo

# How many data points to store for the ping graph
PING_LIMIT = 240

class PingGraph(object):
  '''Handles drawing to the ping graph for the servers'''
  def __init__(self, dic, darea):
    self.darea = darea
    dic['on_ping_graph_draw'] = self.on_ping_graph_draw

    self.data = None

  def set_data(self, data):
    '''Set or switch the source of the data (owned by each Gameserver)'''
    self.data = data

  def queue_draw(self):
    '''Called when the graph should be redrawn--sets it visible and tells Gtk
    to fire on_draw'''
    rect = self.darea.get_allocation()
    self.darea.queue_draw_area(0, 0, rect.width, rect.height)
    self.darea.set_visible(True)

  def on_ping_graph_draw(self, ping_graph, cx):
    '''Actually draw the graph with Cairo'''
    ping_graph.set_visible(self.data != None)
    if not self.data:
      return

    rect = ping_graph.get_allocation()
    
    cx.set_source_rgb(1.0,1.0,1.0)
    cx.paint()

    # Good pings should be green, middle yellow and high red
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

    # Draw corners so we can fill our graph in
    cx.line_to(x, rect.height)
    cx.line_to(0, rect.height)
    cx.fill()


