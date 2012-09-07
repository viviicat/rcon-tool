#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# cbthread - wraps a very simple callback system into threading.Thread.
#            This tries to emulate twisted.threads.deferToThread since twisted aint
#            on python3
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

# Note: Only works with target-type threads for now

import threading
from collections import Iterable

from gi.repository import GObject

class Thread(threading.Thread):
  def __init__(self, target, callback, *args ):
    super(Thread, self).__init__(target=self._thread_wrapper, args=(callback, args))

    self.callbacks = [callback]

    self.usertarget = target

  def addCallback(self, callback):
    self.callbacks.append(callback)

  def _thread_wrapper(self, callback, args):
    '''This is where the thread starts. It calls the target and then sets up the gtk wrapper
    to be called when GObject gets a chance'''
    ret = self.usertarget(*args)
    GObject.idle_add(self._gtk_wrapper, ret)

  def _gtk_wrapper(self, rets):
    '''This is called when the thread has finished and flow has returned to the main thread.
    It calls the user's callbacks in order'''
    for cb in self.callbacks:
      if not isinstance(rets, Iterable):
        rets = (rets,)

      rets = cb(*rets)
