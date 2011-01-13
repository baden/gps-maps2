#!/usr/bin/python
# -*- coding: utf-8 -*-
# dist.py

"""
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator
 
class Client(Protocol):
  def sendMessage(self, msg):
    self.transport.write("%s\n" % msg)
    for i in range(1,5):
      self.transport.write("%d\n" % i)
  def dataReceived(self, data):
    print data
 
def gotProtocol(p):
    p.sendMessage("Hello")
    reactor.callLater(1, p.sendMessage, "world")
    reactor.callLater(2, p.transport.loseConnection)
 
c = ClientCreator(reactor, Client)
c.connectTCP("localhost", 8007).addCallback(gotProtocol)
reactor.run()
"""


import socket

HOST = "localhost"                 # удаленный компьютер (localhost)
PORT = 80              # порт на удаленном компьютере
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.send(u"1234567")
result = sock.recv(1024)
sock.close()
print u"Получено:", result

