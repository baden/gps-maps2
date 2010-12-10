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

class TestMessage(webapp.RequestHandler):
	def post(self):
		from django.utils import simplejson as json
		from google.appengine.api import channel

		uid = self.request.get("uid")


		message = {
			"answer": "ok",
			"text": "Boo",
		}

		channel.send_message(uid, json.dumps(message))

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		self.response.out.write('{"answer": "Boooooooooooo"}')

application = webapp.WSGIApplication(
	[
		('/debug/test-register.*', TestRegister),
		('/debug/msg.*', TestMessage),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
