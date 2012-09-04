# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# recentcommands - manages recently and commonly used rcon commands
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

    cPickle.dump(best_cmds, fcmds)
    fcmds.close()
