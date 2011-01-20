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

import updater

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

		updater.inform('addlog', system.key(), {
			'skey': str(system.key()),
			'time': gpslog.ldate.strftime("%d/%m/%Y %H:%M:%S"),
			'text': gpslog.text,
			'label': gpslog.label,
			'key': "%s" % gpslog.key()
		})	# Информировать всех пользователей, у которых открыта страница Отчеты

		#token = memcache.get("geolast_%s" % str(system.key()))

		self.response.out.write('ADDLOG: OK\r\n')

class Config(webapp.RequestHandler):
	def post(self):
		from datamodel import DBConfig
		#from zlib import compress

		self.response.headers['Content-Type'] = 'application/octet-stream'

		imei = self.request.get('imei', 'unknown')
		system = DBSystem.get_or_create(imei, phone=self.request.get('phone', None), desc=self.request.get('desc', None))

		cmd = self.request.get('cmd', '')
		if cmd == 'save':
			newconfig = DBConfig.get_by_imei(imei)

			config = {}
			for conf in self.request.body.split("\n"):
				params = conf.strip().split()
				if len(params) == 4:
					config[params[0]] = (params[1], params[2], params[3])

			newconfig.config = config #compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			updater.inform('cfgupd', system.key(), {
				'skey': str(system.key())
			})	# Информировать всех пользователей, у которых открыта страница настроек

			self.response.out.write("CONFIG: OK\r\n")
			return

		self.response.out.write("CONFIG: ERROR\r\n")

class Params(webapp.RequestHandler):
	def get(self):
		from datamodel import DBConfig, DBNewConfig
		self.response.headers['Content-Type'] = 'application/octet-stream'

		imei = self.request.get('imei', 'unknown')
		system = DBSystem.get_or_create(imei)

		cmd = self.request.get('cmd')

		if cmd == 'params':
			newconfig = DBNewConfig.get_by_imei(imei)
			configs = newconfig.config
			if configs and (configs != {}):
				#self.response.out.write("<tr><th>date: %s</th></tr>" % dbconfig.cdate)
				#configs = eval(zlib.decompress(newconfig[0].config))
				#configs = eval(dbconfig.strconfig)
				for config, value in configs.items():
					#self.response.out.write("<tr><td>%s:%s</td></tr>" % (config, value))
					self.response.out.write("PARAM %s %s\r\n" % (config, value))
				self.response.out.write("FINISH\r\n")
			else:
				self.response.out.write("NODATA\r\n")

		elif cmd == 'cancel':
			newconfigs = DBNewConfig().get_by_imei(imei)
			newconfigs.config = {}
			newconfigs.put()
			
			#for newconfig in newconfigs:
			#	newconfig.delete()
			self.response.out.write("DELETED")

		elif cmd == 'confirm':
			newconfig = DBNewConfig.get_by_imei(imei)
			newconfigs = newconfig.config

			if newconfigs and (newconfigs != {}):
				saveconfig = DBConfig.get_by_imei(imei)
				config = saveconfig.config

				for pconfig, pvalue in newconfigs.items():
					if pconfig in config:
						config[pconfig] = (config[pconfig][0], pvalue, config[pconfig][2])

				saveconfig.config = config
				saveconfig.put()

				newconfig.config = {}
				newconfig.put()

				self.response.out.write("CONFIRM")

			else:
				self.response.out.write("NODATA")

		elif cmd == 'check':
			newconfigs = DBNewConfig.get_by_imei(imei)
			newconfig = newconfigs.config
			if newconfig and (newconfig != {}):
				self.response.out.write('CONFIGUP\r\n')
			else:
				self.response.out.write('NODATA\r\n')

		else:
			self.response.out.write('CMD_ERROR\r\n')


application = webapp.WSGIApplication(
	[('/', MainPage),
		('/s/.*', StaticPage),
		('/addlog', AddLog),	# Событие, не требующее точной привязки ко времени
		('/config.*', Config),	# Конфигурация системы
		('/params.*', Params),	# Запрос параметров системы, например localhost/params?cmd=check&imei=353358019726996
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
