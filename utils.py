# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# utils - short utility functions for rcontool
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

from twisted.internet import threads

import re, urllib

MY_IP = None

def is_valid_ip(input_str):
  return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_str) is not None

def whatismyip(site='http://ipecho.net/plain'):
  global MY_IP

  def post_fetch(site):
    global MY_IP
    ip = site.read()
    print("Got " + ip)
    # FIXME: better regex is possible
    if is_valid_ip(ip):
      MY_IP = ip
      return ip
    else:
      print("Error: failed to fetch a valid public-facing IP address")
      return None

  if MY_IP:
    return MY_IP, False
  else:
    print("Fetching new copy of public IP from " + site + "...")
    d = threads.deferToThread(urllib.urlopen, site)
    d.addCallback(post_fetch)
    return d, True


