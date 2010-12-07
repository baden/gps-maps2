# -*- coding: utf-8 -*-
import logging

from django.utils import simplejson as json

#from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#from template import TemplatedPage
from datamodel import DBAccounts, DBSystem

API_VERSION = 1.0

class BaseApi(webapp.RequestHandler):
	def parcer(self):
		return {"responseData": None}

	def get(self):
		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		callback = self.request.get('callback')
		
		acckey = self.request.get('acckey', None)
		syskey = self.request.get('syskey', None)
		
		nejson = json.dumps(self.parcer())
		self.response.out.write(callback + "(" + nejson + ")\r")

class Version(BaseApi):
	def parcer(self):
		return {"version": API_VERSION}

class Info(BaseApi):
	def parcer(self):
		from datetime import datetime
		accounts = DBAccounts.all().fetch(100)
		accinfos = []
		for rec in accounts:
			accinfo = {
				"key": str(rec.key()),
				"name": rec.name,
				"user": {
					"email": rec.user.email(),
					"id": rec.user.user_id(),
				},
			}
			lsys = []
			for sys in rec.systems:
				lsys.append({
					"key": str(sys.key()),
					"imei": sys.imei,
					"phone": sys.phone,
					"desc": sys.desc,
					"premium": sys.premium >= datetime.now(),
				})
			accinfo["systems"] = lsys
			accinfos.append(accinfo)
		jsonresp = {
			"info": {
				"accounts": accinfos,
			}
		}
		return jsonresp
		
		#answer(self.response, jsonresp)



application = webapp.WSGIApplication(
	[
	('/api/info.*', Info),
	('/api/version.*', Version),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
