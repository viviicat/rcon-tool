#!/usr/bin/env python

# Rcontool -- an gui tool for linux source rcon administration!
# Copyright (c) 2012 Gavin Langdon

from gi.repository import Gtk 
from gi.repository import GObject


from twisted.internet import gtk3reactor
gtk3reactor.install()

import rcongui
from twisted.internet import reactor

import os
os.chdir("/home/gavin/rcontool")



if __name__ == '__main__':
  GObject.threads_init()
  rcon_gui = rcongui.RconGui()
  reactor.run()
  #Gtk.main()
