# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# servermanager - main class for gui elements relating to servers
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



from gi.repository import Gtk, GObject

from twisted.internet import threads
from twisted.internet import reactor
import twisted.internet.error

import cPickle

import rconserver
import serverlogger
import utils
import recentcommands
import pinggraph

import SourceLib

class ServerTextLog(object):
  def __init__(self, tagtable):
    self.log_buffer = Gtk.TextBuffer(tag_table=tagtable)
    self.pretty_buffer = Gtk.TextBuffer(tag_table=tagtable)

class ServerManager(object):
  '''
  The server manager does all the gui stuff for the servers, and manages
  query threads and other deferred events, as well as the text buffers
  '''
  def __init__(self, builder, dic, gui):
    self.bd = builder
    try:
      prefs = open("servers.pkl", "r")
      self.servers = cPickle.load(prefs)
      prefs.close()

    except:
      self.servers = {}
      print("No pickle found. Will create on close")

    self.recentcmdmgr = recentcommands.RecentCommandManager(self.bd.get_object("recent_commands"))

    self.cur_server = None

    self.textlogs = {}
    self.loggers = {}

    self.text_tags = gui.text_tags

    for s in self.servers.values():
      self.textlogs[s] = ServerTextLog(gui.text_tags)
      d = self.query_server(s)
      d.addCallback(self.on_init_post_query_server, s)


    d = { 'on_rcon_password_icon_press' : self.on_rcon_password_icon_press,
          'on_confirm_add_server_clicked' : self.on_confirm_add_server_clicked,
          'on_act_remove_server_activate' : self.on_act_remove_server_activate,
          'on_rcon_input_activate' : self.on_rcon_input_activate,
          'on_rcon_input_icon_press' : self.on_rcon_input_icon_press,
          'on_rcon_input_changed' : self.on_rcon_input_changed,
          'on_rcon_password_changed' : self.on_rcon_password_changed,
          'on_server_list_cursor_changed' : self.on_server_list_cursor_changed,
          'on_show_rcon_toggle_toggled' : self.on_show_rcon_toggle_toggled,
          'on_stick_to_bottom_toggled' : self.on_stick_to_bottom_toggled,
          'on_expand_player_list_clicked' : self.on_expand_player_list_clicked,
          'on_act_toggle_logging_toggled' : self.on_act_toggle_logging_toggled,
        }

    dic.update(d)

    self.pinggraph = pinggraph.PingGraph(dic, self.bd.get_object("ping_graph"))

  def on_expand_player_list_clicked(self, widget):
    pl = self.bd.get_object("players_window")

    self.bd.get_object("player_expander_arrow").set(Gtk.ArrowType.LEFT if pl.get_visible() else Gtk.ArrowType.RIGHT, Gtk.ShadowType.ETCHED_IN)

    pl.set_visible(not pl.get_visible())

  def log_rcon(self, server, command, threaded=True):
    if not self.cur_server.rcon_connected():
      self.cur_server.set_rcon(self.bd.get_object("rcon_password").get_text())

    if threaded:
      d = threads.deferToThread(self.cur_server.rcon_cmd, command)
      d.addCallback(self.on_log_rcon_finished, command, server)

      return d
    else:
      return self.on_log_rcon_finished(self.cur_server.rcon_cmd(command), command, server)

  def on_log_rcon_finished(self, ret_tuple, command, server):
    success, response = ret_tuple
    response = str(response)

    if self.bd.get_object("show_rcons").get_active():
      self.append_to_log(server, command, 'local')
      self.append_to_log(server, response, 'remote')

    widget = self.bd.get_object("rcon_password")

    if success:
      widget.set_property("secondary-icon-stock", Gtk.STOCK_OK)
    else:
      widget.set_property("secondary-icon-stock", Gtk.STOCK_DIALOG_ERROR)

    if not "Unknown command" in response:
      self.recentcmdmgr.addcmd(command)

    return ret_tuple
  
  def append_to_log(self, server, text, tag):
    if not text:
      return

    if text[-1] != '\n':
      text += '\n'
    self.textlogs[server].log_buffer.insert_with_tags(self.textlogs[server].log_buffer.get_end_iter(), text, self.textlogs[server].log_buffer.get_tag_table().lookup(tag))
    if server is self.cur_server:
      self.stick_check()

  def quit(self):
    prefs = open("servers.pkl", "w")
    cPickle.dump(self.servers, prefs)
    prefs.close()

    self.recentcmdmgr.quit()

  def on_rcon_password_changed(self, widget):
    enabled = widget.get_text() != ""
    self.bd.get_object("rcon_notebook").set_show_tabs(enabled)
    self.bd.get_object("act_toggle_logging").set_sensitive(enabled)
    widget.set_property("secondary-icon-sensitive", enabled)
    widget.set_property("secondary-icon-stock", Gtk.STOCK_DIALOG_AUTHENTICATION)

    self.cur_server.set_rcon(widget.get_text())


  def on_rcon_password_icon_press(self, widget, pos, event):
    self.test_rcon(self.cur_server)

  def test_rcon(self, server):
    if server:
      server.set_rcon(self.bd.get_object("rcon_password").get_text())
      return self.log_rcon(server, "version")
    return False

  def on_confirm_add_server_clicked(self, widget):
    ip = self.bd.get_object("ip_entry").get_text()
    if not ip:
      return

    try:
      port = int(self.bd.get_object("port_entry").get_text())
    except:
      #TODO: error checking
      print("Invalid port")
    self.add_server(ip, port)

  def add_server(self, ip, port):
    gs = rconserver.Gameserver(ip, port)
    sid = self.get_server_sid(gs)
    if not sid in self.servers:
      d = self.query_server(gs)
      d.addCallback(self.on_add_server_post_query, sid, gs)
   
      self.servers[sid] = gs
      self.textlogs[gs] = ServerTextLog(self.text_tags)

      self.bd.get_object("query_label").set_text("Querying server...")
      self.bd.get_object("query_spinner").set_visible(True)
      self.bd.get_object("confirm_add_server").set_sensitive(False)
      self.bd.get_object("query_infobox").set_message_type(Gtk.MessageType.INFO)
    else:
      self.bd.get_object("query_infobox").set_message_type(Gtk.MessageType.WARNING)
      self.bd.get_object("query_label").set_text("Server is already in the list.")
      self.bd.get_object("query_spinner").set_visible(False)

    self.bd.get_object("query_infobox").set_visible(True)


  def on_add_server_post_query(self, ret_tuple, sid, server):
    success, errval = ret_tuple
    if not success:
      self.bd.get_object("query_label").set_text(str(errval))
      self.bd.get_object("query_infobox").set_message_type(Gtk.MessageType.ERROR)
      self.bd.get_object("query_spinner").set_visible(False)
      self.bd.get_object("confirm_add_server").set_sensitive(True)

      self.delete_server(server)

      return

    self.add_server_item(server)

    self.close_server_dialog(self.bd.get_object("add_server_dialog"))

    GObject.timeout_add(1000, self.on_query_timer, server)

  def on_query_timer(self, server):
    if server not in self.servers.values():
      return False

    self.query_server(server)

    return True

  def on_init_post_query_server(self, ret_tuple, server):
    success, errval = ret_tuple
    if success:
      self.add_server_item(server)
      GObject.timeout_add(1000, self.on_query_timer, server)
    else:
      self.delete_server(server)

  def get_server_sid(self, server):
    return self.get_sid(server.ip, server.port)

  def get_sid(self, ip, port):
    return ip + ":" + str(port)

  def on_act_remove_server_activate(self, widget):
    if self.cur_server:
      self.delete_server(self.cur_server)

  def delete_server(self, server):
    self.delete_sid(self.get_server_sid(server))

  def delete_sid(self, sid):
    if sid in self.servers:
      server = self.servers[sid]
      if server is self.cur_server:
        self.cur_server = None
      self.set_logging(server, False)
      server.cleanup()
      if server in self.textlogs:
        del self.textlogs[server]
      if server in self.loggers:
        del self.loggers[server]
      del self.servers[sid]

      store = self.bd.get_object("servers_liststore")
    else:
      print("server with sid '"+sid+"' not found to delete")

    for row in store:
      if store.get_value(row.iter, 0) == sid:
        store.remove(row.iter)
        break


  def query_server(self, server):
    d = threads.deferToThread(server.query)
    d.addCallback(self.on_query_result, server)
    return d

  def on_rcon_input_activate(self, widget):
    text = widget.get_text()
    if text == "" or not self.cur_server:
      return

    self.log_rcon(self.cur_server, text)
    widget.set_text("")

  def on_rcon_input_changed(self, widget):
    widget.set_icon_sensitive(1, widget.get_text())

  def on_rcon_input_icon_press(self, widget, pos, event):
    if widget.get_text():
      self.log_rcon(self.cur_server, 'find ' + widget.get_text())

  def on_act_toggle_logging_toggled(self, widget):
    if not self.cur_server:
      return

    self.set_logging(self.cur_server, widget.get_active())

    widget.set_stock_id(Gtk.STOCK_CONNECT if widget.get_active() else Gtk.STOCK_DISCONNECT)

    if widget.get_active():
      self.bd.get_object("rcon_notebook").set_current_page(1)

  def set_logging(self, server, enabled):
    if enabled == server.logging:
      return

    server.logging = enabled

    if enabled:
      d = self.log_rcon(server, "logaddress_list")
      d.addCallback(self.set_logging_post_list, server)

    elif server in self.loggers:
      self.loggers[server].stopListening()
      del self.loggers[server]


  def set_logging_post_list(self, ret_tuple, server):
    # FIXME: Not sure if this is run in a thread or not... So it potentially hangs the system, but I don't know
    success, response = ret_tuple
    if not success:
      self.bd.get_object("act_toggle_logging").set_active(False)
      return

    s, r = self.log_rcon(server, 'log', False)
    if 'not currently logging' in r:
      self.log_rcon(server, 'log on', False)

    ip = utils.whatismyip()

    for port in range(27020,27100):
      # FIXME: this needs to be done linearly instead of sending all the requests at once, since we get errors
      try:
        self.loggers[server] = reactor.listenUDP(port, SourceLib.SourceLog.SourceLogListener(server.ip, server.port, serverlogger.GameserverLogger(self, server)))
        for line in response.split('\n'):
          if ip in line and str(port) not in line:
            self.log_rcon(server, 'logaddress_del ' + line, False)

        self.log_rcon(server, 'logaddress_add ' + self.get_sid(ip, port), False)
        break

      except twisted.internet.error.CannotListenError:
        print("Could not bind to port "+ str(port) + ", trying "+str(port+1))


  def on_query_result(self, ret_tuple, server):
    '''Called when the query thread gets info about a server'''

    # update ping graph whether or not this query worked
    server.add_ping_history()
    self.pinggraph.queue_draw()

    success, errmsg = ret_tuple
    if not success:
      return ret_tuple

    if self.cur_server and server is self.cur_server:
      self.populate_query_data(server.info)

    store = self.bd.get_object("servers_liststore")

    for row in store:
      if store.get_value(row.iter, 0) == self.get_server_sid(server):
        store.set(row.iter, 1, server.info['hostname'], 2, self.format_numplayers(server.info), 3, server.info['ping'], 4, server.info['map'])
        break


    return ret_tuple

  def stick_check(self):
    '''If we try to stick now, we'll scroll to the pre-calculated 'bottom' of the buffer, which is the
    end of the previous line. So we just defer the stick until the next loop so it'll get taken care of properly.
    Also, we're not using the 'insert mark' that many online have suggested, because if the text is selected it
    sticks to that part of the buffer instead of the bottom. I have yet to find a nice elegant way to do this.
    This way makes for a slight flicker, but it's way better than anything else I've tried'''
    GObject.idle_add(self._stick_check)

  def _stick_check(self):
    widget = self.bd.get_object("server_log_textview")

    if self.bd.get_object("stick_to_bottom").get_active():
      adj = widget.get_vadjustment()
      adj.set_value(adj.get_upper())

  def on_stick_to_bottom_toggled(self, widget):
    if self.cur_server and widget.get_active():
      self.stick_check()

  def populate_selected(self):
    '''update the gui for the selected server'''
    tv = self.bd.get_object("server_log_textview")
    buf = self.textlogs[self.cur_server].log_buffer
    tv.set_buffer(buf)

    self.stick_check()

    self.pinggraph.set_data(self.cur_server.pings)

    tv2 = self.bd.get_object("pretty_log_textview")
    tv2.set_buffer(self.textlogs[self.cur_server].pretty_buffer)

    self.set_show_rcon(self.cur_server.rcon_visible)
    if self.cur_server.rcon_password:
      self.bd.get_object("rcon_password").set_text(self.cur_server.rcon_password)
    else:
      self.bd.get_object("rcon_password").set_text("")

    self.bd.get_object("act_toggle_logging").set_active(self.cur_server.logging)

  def format_numplayers(self, info):
    return str(info['numplayers']) + "/" + str(info['maxplayers'])

  def populate_query_data(self, info):
    labels = ['hostname', 'ip', 'port', 'map', 'gamedesc', 'ping']
    for l in labels:
      if l in info:
        self.bd.get_object(l+"_label").set_text(str(info[l]))

    self.bd.get_object("players_label").set_text(self.format_numplayers(info))


  def on_show_rcon_toggle_toggled(self, widget):
    self.set_show_rcon(widget.get_active())


  def set_show_rcon(self, enabled):
    self.bd.get_object("rcon_password").set_visibility(enabled)
    self.bd.get_object("show_rcon_toggle").set_active(enabled)
    if self.cur_server:
      self.cur_server.set_rcon_visibility(enabled)

  def on_server_list_cursor_changed(self, widget):
    sel = widget.get_selection()
    if sel:
      model, itr = sel.get_selected()
      sid = model.get_value(itr, 0)

      if sid in self.servers:
        self.cur_server = self.servers[sid]
        self.bd.get_object("rcon_notebook").set_sensitive(True)
        self.query_server(self.cur_server)
        self.populate_selected()

        if not self.cur_server.rcon_connected():
          self.bd.get_object("rcon_notebook").set_current_page(0)

        return

    self.bd.get_object("rcon_notebook").set_sensitive(False)


  def add_server_item(self, server):
    store = self.bd.get_object("servers_liststore")
    iter = store.append([self.get_server_sid(server), server.info['hostname'],str(server.info['numplayers']) + "/" + str(server.info['maxplayers']), server.info['ping'], server.info['map']])
    self.bd.get_object("server_list").set_cursor(store.get_path(iter))

  def close_server_dialog(self, widget):
    self.bd.get_object("main_window").set_sensitive(True)
    widget.hide()


