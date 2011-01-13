#!/usr/bin/python
# -*- coding: utf-8 -*-
# dist.py


from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
 
class Server(Protocol):
	def connectionMade(self):
		self.transport.write(self.factory.quote+'\r\n')
	def connectionLost(self, reason):
		print 'connection lost ...'
	def dataReceived(self, data):
		print data
		self.transport.write(data)
  
class ServerFactory(Factory):
	protocol = Server
	def __init__(self, quote=None):
		self.quote = quote 

reactor.listenTCP(8007, ServerFactory("quote"))
reactor.run()
