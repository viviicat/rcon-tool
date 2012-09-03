#!/usr/bin/env python

import SourceLib.SourceLog
import utils
import asyncore

class parser(SourceLib.SourceLog.SourceLogParser):
  def action(self, remote, timestamp, key, value, properties):
    print (remote, timestamp, key, value, properties)
    print ("hi")

  def parse(self, line):
    SourceLib.SourceLog.SourceLogParser.parse(self, line)
    print(line.strip('\x00\xff\r\n\t'))

ip = utils.whatismyip()
rcon = SourceLib.SourceRcon.SourceRcon('fun.critsandvich.com', 27015, 'xe7Zsg')
print (rcon.rcon("logaddress_add " + ip + ":" + "27020"))
print (rcon.rcon("log"))

listener = SourceLib.SourceLog.SourceLogListener(('', 27020), ('fun.critsandvich.com',27015), parser())

asyncore.loop()

