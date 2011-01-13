#!/usr/bin/python
# -*- coding: utf-8 -*-
# dist.py

from twisted.web import resource
class MyGreatResource(resource.Resource):
    def render_GET(self, request):
        return "<html>foo</html>"

resource = MyGreatResource()

print '=== MY.RPY reload ==='
