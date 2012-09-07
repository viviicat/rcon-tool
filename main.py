#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# rcontool - a gui tool for linux source rcon administration in GTK+ and Python
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

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

import os, sys
os.chdir(sys.path[0])

import rcongui

import gtkasync


if __name__ == '__main__':
  GObject.threads_init()
  Gdk.threads_enter()
  rcon_gui = rcongui.RconGui()
  gtkasync.install()
  #reactor.run()
  Gtk.main()
  Gdk.threads_leave()
