# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# serverlogger - parses server logs (tf2 only currently)
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


class GameserverLogger(SourceLib.SourceLog.SourceLogParser):
  def __init__(self, servermanager, server):
    SourceLib.SourceLog.SourceLogParser.__init__(self)
    self.server = server
    self.manager = servermanager

    self.objects = { 'OBJ_SENTRYGUN_MINI' : 'Mini-sentry',
        'OBJ_ATTACHMENT_SAPPER' : 'Sapper',
        'OBJ_DISPENSER' : 'Dispenser',
        'OBJ_SENTRYGUN' : 'Sentry',
        'OBJ_TELEPORTER' : 'Teleporter'
        }

#  def append_prettylog(self, text, tag1=None, tag2=None):
#    if not tag1:
#      self.prettylog.insert_with_tags(self.prettylog.get_end_iter(), text)
#    elif not tag2:
#      self.prettylog.insert_with_tags(self.prettylog.get_end_iter(), text, self.prettylog.get_tag_table().lookup(tag1))
#    else:
#      self.prettylog.insert_with_tags(self.prettylog.get_end_iter(), text, self.prettylog.get_tag_table().lookup(tag1), self.prettylog.get_tag_table().lookup(tag2))
#
#
#  def action(self, remote, timestamp, key,value, properties):
#    def getcolortag(team):
#      return 'team_'+team.lower()
#
#    if key in ['say', 'say_team']:
#      text = value['player_name'] + ": "+value['message']
#      if key == 'say_team':
#        text = '(TEAM) ' + text
#
#      self.append_prettylog(text, getcolortag(value['player_team']), "say")
#
#    elif key == 'kill':
#      self.append_prettylog(value['attacker_name'], getcolortag(value['attacker_team']))
#      self.append_prettylog(" killed ")
#      self.append_prettylog(value['victim_name'], getcolortag(value['victim_team']))
#      self.append_prettylog(" with "+value['weapon'])
#
#    elif key == 'class':
#      self.append_prettylog(value['player_name'], getcolortag(value['player_team']))
#      self.append_prettylog(" changed to "+value['class'])
#      
#    elif key == 'team':
#      self.append_prettylog(value['player_name'])
#      self.append_prettylog(" joined team ")
#      self.append_prettylog(value['team'], getcolortag(value['team']))
#
#    elif key == 'connect':
#      self.append_prettylog(value['player_name'] + " (" + value['player_steamid'] + ") connected from " + value['ip'])
#
#    elif key == 'trigger':
#      if value['trigger'] == 'builtobject':
#        self.append_prettylog(value['player_name'], getcolortag(value['player_team']))
#        self.append_prettylog(" built a " + self.objects[properties['object']])
#
#      elif value['trigger'] == 'killedobject':
#        self.append_prettylog(value['player_name'], getcolortag(value['player_team']))
#        self.append_prettylog(" destroyed ")
#        self.append_prettylog(properties['objectowner']['player_name'] + "'s ", getcolortag(properties['objectowner']['player_team']))
#        self.append_prettylog(self.objects[properties['object']] + " with " + properties['weapon'])
#      else:
#        print(value, properties)
#        return
#    else:
#      return
#
#    self.append_prettylog("\n")
 

  def parse(self, line):
    SourceLib.SourceLog.SourceLogParser.parse(self, line)
    self.manager.append_to_log(self.server, line, 'remote')


