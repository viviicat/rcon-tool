#!/usr/bin/env python

from twisted.internet import threads, reactor

from SourceLib import SourceQuery


def defer(info):
  print (info)
  reactor.stop()

q = SourceQuery.SourceQuery('slay1.critsandvich.com')

d = threads.deferToThread(q.info)
d.addCallback(defer)
for i in range(30):
  print ("hello", i)

reactor.run()
