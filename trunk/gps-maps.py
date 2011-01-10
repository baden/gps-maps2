# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from template import TemplatedPage
import datamodel

#from guppy import hpy

class MainPage(TemplatedPage):
	def get(self):
		#h = hpy()
		#logging.info("Heap: %s" % h.heap())
		template_values = {}
		self.write_template(template_values)

class StaticPage(TemplatedPage):
	def get(self):
		template_values = {}
		#token = channel.create_channel(self.user.user_id())
		#template_values["token"] = token

		self.write_template(template_values, alturl=self.request.path[3:] + ".html")


application = webapp.WSGIApplication(
	[('/', MainPage),
		('/s/.*', StaticPage),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()