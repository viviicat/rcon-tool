# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# server - Class for managing a server in rcontool
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

import SourceLib

import socket

import pinggraph

def get_default_info():
  return { 'ip' : '', 'port' : -1, 'hostname' : '???', 'numplayers' : 0, 'maxplayers' : 0, 'ping' : 1000, 'map' : 'Unknown', 'gamedesc' : 'Unknown'}

class Gameserver(object):
  def __init__(self, ip, port, rcon_visible=False, rcon_password=None, save_rcon=True):
    self.ip = ip
    self.port = port
    self.rcon_visible = rcon_visible
    self.rcon_password = rcon_password
    self.rcon = None

    self.logging = False
    
    self.pings = []

    self.info = get_default_info()
    self.info['ip'] = ip
    self.info['port'] = port

    self.player = []

    self.save_rcon = save_rcon

  def __reduce__(self):
    '''Magical pickle packer, creates a new "gameserver" instance with the following args'''
    return Gameserver, (self.ip,self.port,self.rcon_visible, self.rcon_password if self.save_rcon else None, self.save_rcon)

  def __key(self):
    return (self.ip, self.port)

  def __hash__(self):
    '''Servers should be unique by IP'''
    return self.__key().__hash__()

  def __cmp__(self, other):
    return self.__hash__() < other.__hash__()

  def add_ping_history(self):
    self.pings.append(self.info['ping'])
    if len(self.pings) > pinggraph.PING_LIMIT:
      self.pings.pop(0)

  def rcon_cmd(self, command):
    if not self.rcon_connected():
      return False, "Password not set, ignoring"

    try:
      return True, self.rcon.rcon(command)
    except SourceLib.SourceRcon.SourceRconError as e:
      self.rcon = None
      return False, str(e)
    except socket.gaierror as e:
      self.rcon = None
      return False, str(e)

  def query(self):
    try:
      q = SourceLib.SourceQuery.SourceQuery(self.ip, self.port)
      info = q.info()
      if info:
        self.info.update(info)
      else:
        return False, "Failed to connect to the server"

      player = q.player()
      if len(player):
        self.player = player

      if 'ping' in self.info:
        self.info['ping'] = int(self.info['ping'] * 1000)
      else:
        self.info['ping'] = 9001

      return True, ""
    except (SourceLib.SourceQuery.SourceQueryError, socket.gaierror) as e:
      error = e
    except socket.timeout as e:
      error = "Request timed out"
    except socket.error as e:
      error = e

    self.info['ping'] = 9001
    return False, error

  def cleanup(self):
    if self.rcon_connected():
      self.rcon.disconnect()
    

  def set_rcon_visibility(self, enabled):
    self.rcon_visible = enabled

  def rcon_connected(self):
    return self.rcon != None

  def set_rcon(self, newpass):
    if not newpass:
      return

    if self.rcon_password != newpass or not self.rcon:
      self.rcon_password = newpass
      self.rcon = SourceLib.SourceRcon.SourceRcon(self.ip, self.port, self.rcon_password)


