# -*- coding: utf-8 -*-

import logging

from datamodel import DBGeo

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class GeoPage(webapp.RequestHandler):
	def get(self):
		self.response.out.write("ok.")

application = webapp.WSGIApplication(
	[('/geo/.*', GeoPage),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
