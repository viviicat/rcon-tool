#!/usr/bin/env python 

import socket, asyncore 

class AsyncoreClientUDP(asyncore.dispatcher): 

   def __init__(self, server, port): 
      self.server = server 
      self.port = port 
      self.buffer = "" 

      # Network Connection Magic! 
      asyncore.dispatcher.__init__(self) 
      self.create_socket(socket.AF_INET, socket.SOCK_DGRAM) 
      self.bind( ('', 0) ) # bind to all interfaces and a "random" free port. 
      print "Connecting..." 

   # Once a "connection" is made do this stuff. 
   def handle_connect(self): 
      print "Connected" 
    
   # If a "connection" is closed do this stuff. 
   def handle_close(self): 
      self.close() 

   # If a message has arrived, process it. 
   def handle_read(self): 
      data, addr = self.recv(2048) 
      print data 

   # Actually sends the message if there was something in the buffer. 
   def handle_write(self): 
      if self.buffer != "": 
         print self.buffer 
         sent = self.sendto(self.buffer, (self.server, self.port)) 
         self.buffer = self.buffer[sent:] 

connection = AsyncoreClientUDP("127.0.0.1",5005) # create the "connection" 
while 1: 
   asyncore.loop(count = 10) # Check for upto 10 packets this call? 
   connection.buffer += raw_input(" Chat > ") # raw_input (this is a blocking call)
