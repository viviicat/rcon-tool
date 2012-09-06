# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# servermanager - Manages GUI functions related to servers
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

from gi.repository import Gtk, GObject

from twisted.internet import threads
from twisted.internet import reactor
import twisted.internet.error

import time # If only we had more time
import cPickle

import serverlogger
import utils
import recentcommands
import pinggraph
import addserverdialog

import statusmanager

import SourceLib

# wait 2 seconds between queries (default max queries per second per ip is 3, so let's reduce
# the probability that we'll hit that)
QUERY_DELAY = 2000

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
      d = self.init_server(s)
      d.addCallback(self.on_init_post_query_server, s)


    d = { 'on_rcon_password_icon_press' : self.on_rcon_password_icon_press,
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
          'on_rcon_password_activate' : self.on_rcon_password_activate,
        }

    self.addserverdialog = addserverdialog.AddServerDialog(self, builder, dic)

    dic.update(d)

    self.pinggraph = pinggraph.PingGraph(dic, self.bd.get_object("ping_graph"))

  def add_server(self, server):
    '''Returns a Defer if the server has been added, False otherwise'''
    sid = self.get_server_sid(server)
    if sid in self.servers:
      return False
    
    self.servers[sid] = server
    return self.init_server(server)

  def init_server(self, server):
    self.textlogs[server] = ServerTextLog(self.text_tags)
    return self.query_server(server)

  def on_expand_player_list_clicked(self, expand_player_list):
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

    rcon_password = self.bd.get_object("rcon_password")

    if success:
      rcon_password.set_property("secondary-icon-stock", Gtk.STOCK_OK)
    else:
      rcon_password.set_property("secondary-icon-stock", Gtk.STOCK_DIALOG_ERROR)

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
    cPickle.dump(self.servers, prefs, 2)
    prefs.close()

    self.recentcmdmgr.quit()

  def on_rcon_password_changed(self, rcon_password):
    enabled = rcon_password.get_text() != ""

    self.bd.get_object("rcon_notebook").set_show_tabs(enabled)
    self.bd.get_object("act_toggle_logging").set_sensitive(enabled)
    rcon_password.set_property("secondary-icon-sensitive", enabled)
    rcon_password.set_property("secondary-icon-stock", Gtk.STOCK_DIALOG_AUTHENTICATION)

    self.cur_server.set_rcon(rcon_password.get_text())


  def on_rcon_password_icon_press(self, rcon_password, pos, event):
    self.test_rcon(self.cur_server)

  def test_rcon(self, server):
    if server:
      server.set_rcon(self.bd.get_object("rcon_password").get_text())
      d = self.log_rcon(server, "version")
      d.addCallback(self.test_rcon_cb)
      return d
    return False

  def test_rcon_cb(self, ret_tuple):
    success, response = ret_tuple
    if success:
      statusmanager.push_status("RCON Password test succeeded.")
    else:
      statusmanager.push_status("RCON Password test failed.")

    return ret_tuple

  def on_rcon_password_activate(self, rcon_password):
    self.test_rcon(self.cur_server)


  def on_query_timer(self, server):
    if server not in self.servers.values():
      return False

    self.query_server(server)

    return True

  def init_query_timer(self, server):
    GObject.timeout_add(QUERY_DELAY, self.on_query_timer, server)

  def on_init_post_query_server(self, ret_tuple, server):
    success, errval = ret_tuple

    self.add_server_item(server, success)
    self.init_query_timer(server)

  def get_server_sid(self, server):
    return self.get_sid(server.ip, server.port)

  def get_sid(self, ip, port):
    return ip + ":" + str(port)

  def on_act_remove_server_activate(self, act_remove_server):
    if self.cur_server:
      sid = self.get_server_sid(self.cur_server)
      self.delete_sid(sid)
      statusmanager.push_status("Deleted server "+sid+".")

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

    else:
      msg = "Server with sid '"+sid+"' not found to delete."
      print(msg)
      statusmanager.push_status(msg)

    store = self.bd.get_object("servers_liststore")
    for row in store:
      if store.get_value(row.iter, 0) == sid:
        store.remove(row.iter)
        break


  def query_server(self, server):
    d = threads.deferToThread(server.query)
    d.addCallback(self.on_query_result, server)
    return d

  def on_rcon_input_activate(self, rcon_input):
    text = rcon_input.get_text()
    if text == "" or not self.cur_server:
      return

    self.log_rcon(self.cur_server, text)
    rcon_input.set_text("")

  def on_rcon_input_changed(self, rcon_input):
    rcon_input.set_icon_sensitive(1, rcon_input.get_text())

  def on_rcon_input_icon_press(self, rcon_input, pos, event):
    if rcon_input.get_text():
      self.log_rcon(self.cur_server, 'find ' + rcon_input.get_text())

  def on_act_toggle_logging_toggled(self, act_toggle_logging):
    if not self.cur_server:
      return

    self.set_logging(self.cur_server, act_toggle_logging.get_active())

    act_toggle_logging.set_stock_id(Gtk.STOCK_CONNECT if act_toggle_logging.get_active() else Gtk.STOCK_DISCONNECT)

    if act_toggle_logging.get_active():
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
      statusmanager.push_status("Disabled logging from "+self.get_server_sid(server)+".")


  def set_logging_post_list(self, ret_tuple, server):
    # FIXME: This is not run in a thread, so it hangs the system if connecting takes a while.
    success, response = ret_tuple
    if not success:
      self.bd.get_object("act_toggle_logging").set_active(False)
      return

    s, r = self.log_rcon(server, 'log', False)
    if 'not currently logging' in r:
      self.log_rcon(server, 'log on', False)

    def after_fetch_ip(ip):
      if not ip:
        return

      for port in xrange(27020,27100):
        try:
          self.loggers[server] = reactor.listenUDP(port, SourceLib.SourceLog.SourceLogListener(server.ip, server.port, serverlogger.GameserverLogger(self, server)))
          for line in response.split('\n'):
            if ip in line and str(port) not in line:
              self.log_rcon(server, 'logaddress_del ' + line, False)

          self.log_rcon(server, 'logaddress_add ' + self.get_sid(ip, port), False)
          statusmanager.push_status("Enabled logging from "+self.get_server_sid(server)+".")
          break

        except twisted.internet.error.CannotListenError:
          print("Could not bind to port "+ str(port) + ", trying "+str(port+1))


    ret, thread = utils.whatismyip()
    if thread:
      ret.addCallback(after_fetch_ip)
    else:
      after_fetch_ip(ret)


  def on_query_result(self, ret_tuple, server):
    '''Called when the query thread gets info about a server'''
    success, errmsg = ret_tuple

    # update ping graph whether or not this query worked
    server.add_ping_history()
    self.pinggraph.queue_draw()

    store = self.bd.get_object("servers_liststore")


    for row in store:
      if store.get_value(row.iter, 0) == self.get_server_sid(server):
        store.set(row.iter, 1, server.info['hostname'], 2, self.format_numplayers(server.info), 3, server.info['ping'], 4, server.info['map'], 5, Gtk.STOCK_CONNECT if success else Gtk.STOCK_DISCONNECT)
        break

    if success and self.cur_server and server is self.cur_server:
      self.populate_query_data(server.info, server.player)

    return ret_tuple

  def stick_check(self):
    '''If we try to stick now, we'll scroll to the pre-calculated 'bottom' of the buffer, which is the
    end of the previous line. So we just defer the stick until the next loop so it'll get taken care of properly.
    Also, we're not using the 'insert mark' that many online have suggested, because if the text is selected it
    sticks to that part of the buffer instead of the bottom. I have yet to find a nice elegant way to do this.
    This way makes for a slight flicker, but it's way better than anything else I've tried'''
    GObject.idle_add(self._stick_check)

  def _stick_check(self):
    log_tv = self.bd.get_object("server_log_textview")

    if self.bd.get_object("stick_to_bottom").get_active():
      adj = log_tv.get_vadjustment()
      adj.set_value(adj.get_upper())

  def on_stick_to_bottom_toggled(self, stick_to_bottom):
    if self.cur_server and stick_to_bottom.get_active():
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

  def populate_query_data(self, info=[], players=[]):
    def get_play_time_string(seconds):
      return time.strftime('%H:%M:%S', time.gmtime(seconds))

    labels = ['hostname', 'ip', 'port', 'map', 'gamedesc', 'ping']
    for l in labels:
      self.bd.get_object(l+"_label").set_text(str(info[l]) if l in info else "")

    self.bd.get_object("players_label").set_text(self.format_numplayers(info) if info else "")
      
    store = self.bd.get_object("players_liststore")
    # handle the case where we have players already in the list
    # by setting instead of deleting and adding, we should avoid deselection or messiness
    for row in store:
      p_index = store.get_value(row.iter, 0)
      if p_index < len(players):
        plr = players[p_index]
        # time is in seconds, convert to h:m:s (this mods by one day, oh noes)
        store.set(row.iter, 1, plr['name'], 2, plr['kills'], 3, get_play_time_string(plr['time']))
      else:
        # handle the case where a player on the list has left
        store.remove(row.iter)
    # handle the case where a player has joined
    if len(players) > len(store):
      for i in xrange(len(store), len(players)):
        player = players[i]
        store.append([i, player['name'], player['kills'], get_play_time_string(player['time'])])

  def on_show_rcon_toggle_toggled(self, show_rcon_toggle):
    self.set_show_rcon(show_rcon_toggle.get_active())


  def set_show_rcon(self, enabled):
    self.bd.get_object("rcon_password").set_visibility(enabled)
    self.bd.get_object("show_rcon_toggle").set_active(enabled)
    if self.cur_server:
      self.cur_server.set_rcon_visibility(enabled)

  def on_server_list_cursor_changed(self, server_list):
    sel = server_list.get_selection()
    if sel:
      model, itr = sel.get_selected()
      if itr:
        sid = model.get_value(itr, 0)

        if sid in self.servers:
          self.cur_server = self.servers[sid]
          self.bd.get_object("rcon_notebook").set_sensitive(True)
          self.query_server(self.cur_server)
          self.populate_selected()

          if not self.cur_server.rcon_connected():
            self.bd.get_object("rcon_notebook").set_current_page(0)

          self.bd.get_object("act_remove_server").set_sensitive(True)
          return

    self.clear_server_display()

  def clear_server_display(self):
    self.bd.get_object("rcon_notebook").set_sensitive(False)
    self.populate_query_data()
    self.pinggraph.set_data(None)
    self.bd.get_object("act_toggle_logging").set_sensitive(False)
    self.bd.get_object("act_remove_server").set_sensitive(False)

  def add_server_item(self, server, connected=True):
    store = self.bd.get_object("servers_liststore")
    iter = store.append([self.get_server_sid(server), server.info['hostname'],str(server.info['numplayers']) + "/" + str(server.info['maxplayers']), server.info['ping'], server.info['map'], Gtk.STOCK_CONNECT if connected else Gtk.STOCK_DISCONNECT])
    self.bd.get_object("server_list").set_cursor(store.get_path(iter))



