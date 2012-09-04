# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# utils - short utility functions for rcontool
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
