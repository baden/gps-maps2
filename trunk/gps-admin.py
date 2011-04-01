# -*- coding: utf-8 -*-
#import cgi
#from google.appengine.tools.dev_appserver import datastore
import logging
import os
#import zlib
#import math
import utils

#from datetime import date
#from datetime import datetime
from datetime import date, timedelta, datetime

#from django.utils import simplejson as json
#from google.appengine.api import users
from google.appengine.api import datastore
#from google.appengine.api import urlfetch
#from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.tools import bulkloader

# Must set this env var *before* importing any part of Django.
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#TIME_ZONE = 'America/Los_Angeles'  # i.e., Mountain View
#from google.appengine.ext.webapp import template

#import models

#ADMIN_USERNAME = 'baden.i.ua'

SERVER_NAME = os.environ['SERVER_NAME']

#OLDDATA = timedelta(days=30)

class AdminFlushOld(webapp.RequestHandler):
	def get(self):
		#db.delete(datamodel.DBGPSPoint.all(keys_only=True).filter("date <", datetime.utcnow() - OLDDATA).order('date').fetch(100))
		#self.redirect('/admin.data')
		pass

class AdminFlushOld2(webapp.RequestHandler):
	def get(self):
		from datamodel import DBGPSBinBackup

		old = timedelta(days=int(self.request.get("old", "30")))
		logging.info('Old=%s' % repr(old))

		db.delete(DBGPSBinBackup.all(keys_only=True).filter("cdate <=", datetime.utcnow() - old).order('cdate').fetch(500))
		#self.redirect('/admin.data')

application = webapp.WSGIApplication(
	[
	('/admin.flushold', AdminFlushOld),
	('/admin.flushold2', AdminFlushOld2),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
