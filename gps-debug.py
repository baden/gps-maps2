# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from template import TemplatedPage
from datamodel import DBAccounts, DBSystem

class TestRegister(TemplatedPage):
	def get(self):
		imei = self.request.get("imei", "000")

		self.account.RegisterSystem(imei)

		self.redirect('/')


application = webapp.WSGIApplication(
	[('/debug/test-register.*', TestRegister),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
