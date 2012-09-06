#!/usr/bin/env python

import asyncore, socket 

class AsyncoreServerUDP(asyncore.dispatcher): 
   def __init__(self): 
      asyncore.dispatcher.__init__(self) 

      # Bind to port 5005 on all interfaces 
      self.create_socket(socket.AF_INET, socket.SOCK_DGRAM) 
      self.bind(('', 27020)) 

   # Even though UDP is connectionless this is called when it binds to a port 
   def handle_connect(self): 
      print "Server Started..." 
      self.sendto('hello', ('fun.critsandvich.com', 27015))

   # This is called everytime there is something to read 
   def handle_read(self): 
      data, addr = self.recvfrom(2048) 
      print str(addr)+" >> "+data 

   # This is called all the time and causes errors if you leave it out. 
   def handle_write(self): 
      pass 

AsyncoreServerUDP() 
asyncore.loop()
