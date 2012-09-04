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



import re, urllib

MY_IP = None

def is_valid_ip(input_str):
  return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_str) is not None

def whatismyip(site='http://ipecho.net/plain'):
  global MY_IP

  if not MY_IP:
    print("Fetching new copy of public IP from " + site + "...")
    MY_IP = urllib.urlopen(site).read()
    print("Got " + MY_IP)

  # FIXME: better regex is possible
  if is_valid_ip(MY_IP):
    return MY_IP
  else:
    print("Error: failed to fetch a valid public-facing IP address")
    return None
