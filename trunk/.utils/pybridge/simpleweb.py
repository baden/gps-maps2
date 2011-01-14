#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet import reactor

class Hello(Resource):
    isLeaf = True
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        return "<html>Hello, world! I am located at %r.</html>" % repr(request)

resource = Hello()

root = Hello()
root.putChild('fred', Hello())
root.putChild('bob', Hello())

class Simple(Resource):
    isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
"""

from twisted.internet import reactor
from twisted.web import static, server, twcgi


from twisted.web.resource import Resource

class MyResource(Resource):
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

resource = MyResource()


root = static.File("./htdocs")
root.putChild("rc", resource)
reactor.listenTCP(8080, server.Site(root))
reactor.run()
