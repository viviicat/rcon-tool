# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# addserverdialog - dialog for adding servers!
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

from gi.repository import Gtk

import server, statusmanager

DEFAULT_PORT = 27015

class AddServerDialog(object):
  def __init__(self, manager, builder, dic):
    self.ip_entry = builder.get_object("ip_entry")
    self.port_entry = builder.get_object("port_entry")

    self.query_spinner = builder.get_object("query_spinner")
    self.query_infobox = builder.get_object("query_infobox")
    self.query_label = builder.get_object("query_label")

    self.window = builder.get_object("add_server_dialog")
    self.main_window = builder.get_object("main_window")

    self.confirm_add_server = builder.get_object("confirm_add_server")

    self.manager = manager

    d = { 'on_confirm_add_server_clicked' : self.on_confirm_add_server_clicked,
        'on_add_server_dialog_delete_event' : self.on_add_server_dialog_delete_event,
        'on_cancel_add_server_clicked' : self.on_cancel_add_server_clicked,
        'on_act_add_server_activate' : self.on_act_add_server_activate,
        'on_ip_entry_changed' : self.on_ip_entry_changed,
        }

    dic.update(d)

  def on_confirm_add_server_clicked(self, confirm_add_server):
    ip = self.ip_entry.get_text().strip()
    err = ""
    if not ip:
      err = "Please enter a valid IP."

    if not self.port_entry.get_text().strip():
      self.port_entry.set_text("27015")

    try:
      port = int(self.port_entry.get_text().strip())
    except:
      if err:
        err += "\n"
      err += "Please enter a valid port."

    if err:
      self.send_message(err, "error")
      return

    self.add_server(ip, port)

  def send_message(self, text="", msg_type="info"):
    self.query_infobox.set_visible(text != "")

    if not text:
      return


    types = {"load" : Gtk.MessageType.INFO, 
             "info" : Gtk.MessageType.INFO, 
             "error" : Gtk.MessageType.ERROR, 
             "warning" : Gtk.MessageType.WARNING}

    if msg_type not in types:
      msg_type = "info"

    self.query_infobox.set_message_type(types[msg_type])

    self.query_label.set_text(text)
    self.query_spinner.set_visible(msg_type=="load")


  def add_server(self, ip, port):
    gs = server.Gameserver(ip, port)
    d = self.manager.add_server(gs)
    if d:
      d.addCallback(self.on_add_server_post_query, gs)
   
      self.send_message("Querying server...", "load")
      self.confirm_add_server.set_sensitive(False)
    else:
      self.send_message("Server is already in the list.", "warning")

  def on_add_server_post_query(self, ret_tuple, server):
    success, errval = ret_tuple
    if not success:
      self.send_message(str(errval), "error")
      self.confirm_add_server.set_sensitive(True)
      self.manager.delete_server(server)
      return

    statusmanager.push_status("Added server "+self.manager.get_server_sid(server)+".")
    self.manager.add_server_item(server)
    self.close_server_dialog(self.window)

    self.manager.init_query_timer(server)

  def close_server_dialog(self, server_dialog):
    self.main_window.set_sensitive(True)
    server_dialog.hide()

  def on_act_add_server_activate(self, act_add_server):
    self.main_window.set_sensitive(False)
    self.ip_entry.set_text("")
    self.ip_entry.grab_focus()
    self.port_entry.set_text("27015")
    self.send_message("Please enter the new server's IP and port.", "info")
    self.confirm_add_server.set_sensitive(True)

    self.window.show()

  def on_cancel_add_server_clicked(self, cancel_add_server):
    # get_window doesn't work here--next time it tries to show it fails. not sure why...
    self.close_server_dialog(cancel_add_server.get_toplevel())

  def on_add_server_dialog_delete_event(self, add_server_dialog, event):
    self.close_server_dialog(add_server_dialog)
    return True

  def on_ip_entry_changed(self, ip_entry):
    '''Ensures if the user tries to type a port the contents get redirected to the port field'''
    text = ip_entry.get_text()
    if ":" not in text:
      return

    port_index = text.index(":")
    port_str = text[port_index+1:]

    ip_entry.set_text(text[:port_index])
    if port_str:
      self.port_entry.set_text(port_str)

    self.port_entry.grab_focus()


