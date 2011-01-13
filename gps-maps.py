# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
#from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from template import TemplatedPage
from datamodel import DBSystem, GPSLogs
from google.appengine.api import memcache

#from guppy import hpy

class MainPage(TemplatedPage):
	def get(self):
		#h = hpy()
		#logging.info("Heap: %s" % h.heap())
		template_values = {}
		self.write_template(template_values)

#class updater():
#	def _log():
#		return 'aaa'
#	log = _log


"""
	Информирование клиента о обновлении данных
	Нужно перебрать всех подключенных клиентов, у кого есть данная системы и оповестить их об обновлении данных.
"""

class StaticPage(TemplatedPage):
	def get(self):
		template_values = {}
		#token = channel.create_channel(self.user.user_id())
		#template_values["token"] = token

		#memcache.set("token_%s" % self.user.user_id(), token)
		#logging.info("SET Memcache key for token: token_%s = %s" % (self.user.user_id(), token))
		#memcache.set("token_last", token)
		#memcache.set("token_last_cid", self.user.user_id())

		self.write_template(template_values, alturl=self.request.path[3:] + ".html")

class AddLog(webapp.RequestHandler):
	def get(self):
		import updater

		self.response.headers['Content-Type'] = 'application/octet-stream'
		system = DBSystem.get_or_create(self.request.get('imei', 'unknown'))

		#uimei = self.request.get('imei')
		#ukey = self.request.get('ukey')
		#uid = self.request.get('uid')
		text = self.request.get('text', 'No text')
		#label = self.request.get('label')
		label = 0
		if text[0:3] == '(1)':
			label = 1
			text = text[3:]
		if text[0:3] == '(2)':
			label = 2
			text = text[3:]
		if text[0:3] == '(3)':
			label = 3
			text = text[3:]

		#newconfigs = datamodel.DBNewConfig.all().filter('user = ', userdb).fetch(1)
		#if newconfigs:
		#	self.response.out.write('CONFIGUP\r\n')

		gpslog = GPSLogs(parent = system, text = text, label = label)
		gpslog.put()
		#set_loglastkey(str(userdb.key()), gpslog.key())

		memcache.set("lastlogkey_%s" % system.key(), "%s" % gpslog.key())
		logging.info("SET Memcache key: lastlogkey_%s = %s" % (system.key(), gpslog.key()))

		updater.inform('addlog', system, text)	# Информировать всех пользователей, у которых открыта страница Отчеты

		#token = memcache.get("geolast_%s" % str(system.key()))

		self.response.out.write('ADDLOG: OK\r\n')


application = webapp.WSGIApplication(
	[('/', MainPage),
		('/s/.*', StaticPage),
		('/addlog', AddLog),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
