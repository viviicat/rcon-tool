# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# statusmanager - manages status bar
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

# not sure if python singletons are frowned upon, but...

from gi.repository import GObject


MESSAGE_DISPLAY_TIME = 2000


class StatusManager(object):
  '''Gtk statusbars are a pain, so this manager just displays a message for some 
  time and then pops if off the stack'''
  def __init__(self):
    self.statusbar = None
    self.timer = None
    self.msgs = 0
    pass


  def time_to_pop(self):
    self.statusbar.pop(0)
    self.msgs -= 1
    if self.msgs <= 0:
      self.msgs = 0
      return False

    return True


self = StatusManager()

def push_status(message):
  if self.timer:
    GObject.source_remove(self.timer)
  self.timer = GObject.timeout_add(MESSAGE_DISPLAY_TIME, self.time_to_pop)

  self.statusbar.push(0, message)
  self.msgs += 1


def set_statusbar(statusbar):
  self.statusbar = statusbar


