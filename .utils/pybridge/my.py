#!/usr/bin/python
# -*- coding: utf-8 -*-
# dist.py

from twisted.web.resource import Resource

class MyResource(Resource):
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

resource = MyResource()

print 'MY.RPY reload'
