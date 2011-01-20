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

		updater.inform('addlog', system.key(), {
			'skey': str(system.key()),
			'time': gpslog.ldate.strftime("%d/%m/%Y %H:%M:%S"),
			'text': gpslog.text,
			'label': gpslog.label,
			'key': "%s" % gpslog.key()
		})	# Информировать всех пользователей, у которых открыта страница Отчеты

		#token = memcache.get("geolast_%s" % str(system.key()))

		self.response.out.write('ADDLOG: OK\r\n')

class Config(TemplatedPage):
	def get(self):
		cmd = self.request.get('cmd')
		uimei = self.request.get('imei')

		userdb = getUser(self.request)
		#logging.debug(userdb.imei)

		if userdb == None:
			#allusers = datamodel.DBUser.all().fetch(100)
			#accounts = datamodel.DBAccounts().all().filter('user =', self.user).fetch(1)
			#allusers = []
			#for account in self.account.systems:
			#	allusers.append(db.get(db.Key(account)))

			#path = os.path.join(os.path.dirname(__file__), 'svg', 'cars')
			#flist = os.listdir('/')

			template_values = {
				'now': datetime.now(),
				#'path': path,
				#'flist': flist,
			}

			#path = os.path.join(os.path.dirname(__file__), 'templates/config.html')
			#self.response.out.write(template.render(path, template_values))

			#template_values = {}
			self.write_template(template_values)
		else:
			if cmd == 'last':
				#self.response.out.write('<html><head><link type="text/css" rel="stylesheet" href="stylesheets/main.css" /></head><body>CONFIG:<br><table>')
				#self.response.out.write(u"<tr><th>Имя</th><th>Тип</th><th>Значение</th><th>Заводская установка</th></tr>" )

				showall = self.request.get('showall')

				descriptions = datamodel.DBDescription().all() #.fetch(MAX_TRACK_FETCH)

				descs={}
				fdescs={}
				for description in descriptions:
					descs[description.name] = description.value
					fdescs[description.name] = description
					pass

				newconfig = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
				#for dbconfig in newconfig:
				if newconfig:
					#self.response.out.write("<tr><th>date: %s</th></tr>" % dbconfig.cdate)
					configs = eval(zlib.decompress(newconfig[0].config))
					#configs = sortDict(eval(zlib.decompress(newconfig[0].config)))

					#configs = eval(dbconfig.strconfig)

					#try:
					#	for config, value in configs.items():
					#		self.response.out.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (config, value[0], value[1], value[2]))
					#except:
					#	self.response.out.write("<tr><td>orig:%s</td></tr>" % repr(configs))

					waitconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
					if waitconfigs:
						waitconfig = eval(zlib.decompress(waitconfigs[0].config))
					else:
						waitconfig = {}

					nconfigs = {}

					for config, value in configs.items():
						#desc = u"Нет описания"
						desc = u"Нет описания"
						fdesc = None
						if config in descs:
							desc = descs[config]
							fdesc = fdescs[config]
						else:
							if not showall:
							#if not users.is_current_user_admin():
								continue

						if config in waitconfig:
							nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], waitconfig[config], desc, fdesc)
						else:
							nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], None, desc, fdesc)
							#configs[config] = (configs[config][0], configs[config][1], configs[config][2], configs[config][1])

					# Для удобства отсортируем словарь в список
					#sconfigs = sortDict(configs)
					sconfigs = [(key, nconfigs[key]) for key in sorted(nconfigs.keys())]

					template_values = {
					    'configs': sconfigs,
					    'user': userdb,
					    'imei': uimei
					}

					#path = os.path.join(os.path.dirname(__file__), 'templates/config-last.html')
					#self.response.out.write(template.render(path, template_values))
					self.write_template(template_values, alturl='config-last.html')
				else:
					self.response.out.write(u"<html><body>Нет записей</body></html>")
					#self.response.out.write("</table></body></html>")

			else:
				template_values = {
				    'configs': conf_parms,
				    'user': userdb,
				    'imei': uimei
				}

				path = os.path.join(os.path.dirname(__file__), 'templates/params.html')
				self.response.out.write(template.render(path, template_values))

		#DBNewConfig

	def post(self):
		userdb = getUser(self.request, create=True)
		if not userdb:
			self.response.out.write("NO USER")
			return

		cmd = self.request.get('cmd')
		if cmd == 'save':
			#self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
			self.response.headers['Content-Type'] = 'application/octet-stream'
			newconfigs = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				#Подавим объединение конфигураций
				config = {}
				#config = eval(zlib.decompress(newconfig.config))
				##config = eval(newconfig.strconfig)
			else:
				newconfig = datamodel.DBConfig()
				newconfig.user = userdb
				config = {}

			#logging.info(self.request.body)
			for conf in self.request.body.split("\n"):
				params = conf.strip().split()
				#logging.info(params)
				if len(params) == 4:
					config[params[0]] = (params[1], params[2], params[3])
				#self.response.out.write("<tr><td>parts:%s</td></tr>" % repr(conf.strip()))

			#newconfig = DBConfig()
			#newconfig.user = userdb
			newconfig.config = zlib.compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			self.response.out.write("CONFIG: OK\r\n")

			pass
		else:

			self.response.out.write("<html><body>\r\n")

			config = self.request.get('userconfig') + ";" + self.request.get('custom')
			params = config.split(';')

			self.response.out.write("Config: %s<br/>" % config)

			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				config = eval(zlib.decompress(newconfig.config))
				#config = eval(newconfig.strconfig)
			else:
				newconfig = datamodel.DBNewConfig()
				newconfig.user = userdb
				config = {}

			for param in params:
				item = param.split('=')
				if len(item) == 2:
					config[item[0]] = item[1]

			newconfig.config = zlib.compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			if len(config) != 0:
				self.response.out.write("Params: %d" % len(config))

			self.response.out.write("</body></html>")



application = webapp.WSGIApplication(
	[('/', MainPage),
		('/s/.*', StaticPage),
		('/addlog', AddLog),	# Событие, не требующее точной привязки ко времени
		('/config.*', Config),	# Конфигурация системы
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
