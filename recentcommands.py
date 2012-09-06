# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# recentcommands - manages recently and commonly used rcon commands
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



import cPickle

MAX_CMDS = 25

class RecentCommandManager(object):
  def __init__(self, store):
    self.store = store
    self.commands = {}
    try:
      fcmds = open("recentcommands.pkl", "r")
      cmds = cPickle.load(fcmds)
      for cmd, val in cmds:
        self.commands[cmd] = val
        self.add_to_store(cmd)
      fcmds.close()

    except:
      pass


  def add_to_store(self, cmd):
    self.store.append([cmd])


  def addcmd(self, command):
    command = command.strip()

    if not command in self.commands:
      self.commands[command] = 0
      self.add_to_store(command)
    else:
      self.commands[command] += 1


  def quit(self):
    fcmds = open("recentcommands.pkl", "w")

    best_cmds = [tup for tup in sorted(self.commands.iteritems(), key=lambda(k, v) : (v, k))][:MAX_CMDS]

    cPickle.dump(best_cmds, fcmds, 2)
    fcmds.close()
