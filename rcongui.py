# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# rcongui - Manages the main GUI functions for rcontool
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

from twisted.internet import reactor

import servermanager
import statusmanager


class RconGui:
  '''Manages the main GUI functions for rcontool'''
  def __init__(self):
    self.bd = Gtk.Builder()
    self.bd.add_from_file("rcontool.glade")
    self.win = self.bd.get_object("main_window")

    nb = self.bd.get_object("server_info_box")
    # Force this box to stay small since it likes to expand
    nb.set_property("expand", False) 

    self.text_tags = self.bd.get_object("text_tags")

    self.setup_toolbar()
    statusmanager.set_statusbar(self.bd.get_object("statusbar"))

    dic = { 
        'on_about_dialog_delete_event' : self.on_about_dialog_delete_event,
        'on_about_dialog_response' : self.on_about_dialog_response,
        'on_main_window_destroy' : self.on_main_window_destroy,
        'on_server_list_button_press_event' : self.on_server_list_button_press_event,
        'on_act_quit_activate' : self.on_act_quit_activate,
        'on_about_menuitem_activate' : self.on_about_menuitem_activate,
    }

    self.servermanager = servermanager.ServerManager(self.bd, dic, self)

    self.bd.connect_signals(dic)

    self.win.show()

  def setup_toolbar(self):
    '''Manually create a toolbar since Glade doesn't properly support 
    PRIMARY_TOOLBAR style'''
    addbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_ADD, label="Add Server...", is_important=True)
    addbutton.set_related_action(self.bd.get_object("act_add_server"))
    addbutton.set_use_action_appearance(True)
    removebutton = Gtk.ToolButton(stock_id=Gtk.STOCK_REMOVE, label="Remove Server")
    removebutton.set_related_action(self.bd.get_object("act_remove_server"))
    removebutton.set_use_action_appearance(True)

    separator = Gtk.SeparatorToolItem(draw=False)
    separator.set_expand(True)

    log_switch = Gtk.ToggleToolButton()
    log_switch.set_related_action(self.bd.get_object("act_toggle_logging"))
    log_switch.set_use_action_appearance(True)

    toolbar = Gtk.Toolbar()
    toolb_style = toolbar.get_style_context()
    toolb_style.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

    toolbar.insert(addbutton, 0)
    toolbar.insert(removebutton, 1)
    toolbar.insert(separator, 2)
    toolbar.insert(log_switch, 3)
    toolbar.show_all()
    slot = self.bd.get_object("manual_toolbar_slot")
    slot.set_property("expand", False)
    slot.pack_start(toolbar, False, True, 0)

  def on_server_list_button_press_event(self, treeview, event):
    # If the user right clicks, show them a menu
    if event.button == 3:
      x = int(event.x)
      y = int(event.y)
      pthinfo = treeview.get_path_at_pos(x, y)
      # If the user has a server in mind, show the server menu
      if pthinfo is not None:
        path, col, cellx, celly = pthinfo
        treeview.grab_focus()
        treeview.set_cursor( path, col, 0)
        self.bd.get_object("server_menu").popup(None, None, None, None, event.button, event.time)
      # Otherwise we just need to show the add server menu
      else:
        self.bd.get_object("add_server_menu").popup(None, None, None, None, event.button, event.time)
      return True


  def on_cancel_add_server_clicked(self, cancel_add_server):
    # get_window doesn't work here--next time it tries to show it fails. not sure why...
    self.servermanager.close_server_dialog(cancel_add_server.get_toplevel())

  def on_add_server_dialog_delete_event(self, add_server_dialog, event):
    self.servermanager.close_server_dialog(add_server_dialog)
    return True

  def on_about_dialog_delete_event(self, about_dialog, event):
    about_dialog.hide()
    return True

  def on_about_menuitem_activate(self, about_menuitem):
    self.bd.get_object("about_dialog").show()

  def on_about_dialog_response(self, about_dialog, response_id):
    about_dialog.hide()


  def on_main_window_destroy(self, main_window):
    self.quit()

  def on_act_quit_activate(self, act_quit):
    self.quit()

  def quit(self):
    self.servermanager.quit()
    print("stopping reactor")
    reactor.stop()
