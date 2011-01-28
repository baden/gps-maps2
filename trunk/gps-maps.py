# -*- coding: utf-8 -*-

__author__ = "Batrak Denis"

import logging

from google.appengine.ext import db
#from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'

from django.conf import settings
settings._target = None
from django.utils import translation
"""

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
		from datamodel import DBNewConfig

		self.response.headers['Content-Type'] = 'application/octet-stream'

		imei = self.request.get('imei', 'unknown')
		system = DBSystem.get_or_create(imei)

		text = self.request.get('text', 'No text')
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

		newconfigs = DBNewConfig.get_by_imei(imei)
		newconfig = newconfigs.config
		if newconfig and (newconfig != {}):
			self.response.out.write('CONFIGUP\r\n')

		gpslog = GPSLogs(parent = system, text = text, label = label)
		gpslog.put()

		#memcache.set("lastlogkey_%s" % system.key(), "%s" % gpslog.key())
		#logging.info("SET Memcache key: lastlogkey_%s = %s" % (system.key(), gpslog.key()))

		updater.inform('addlog', system.key(), {
			'skey': str(system.key()),
			'time': gpslog.ldate.strftime("%d/%m/%Y %H:%M:%S"),
			'text': text,
			'label': label,
			'key': "%s" % gpslog.key()
		})	# Информировать всех пользователей, у которых открыта страница Отчеты

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


class BinBackup(TemplatedPage):

	def fix_bin(pdata):
		from utils import CRC16
		if ((len(pdata)-2) & 31) != 0:
			while (len(pdata) & 31)!=0:
				pdata += chr(0)
		if (len(pdata) & 31)==0:
			crc = 0
			for byte in pdata:
				crc = CRC16(crc, ord(byte))
			pdata += chr(crc & 0xFF)
			pdata += chr((crc>>8) & 0xFF)
		return pdata

	def get(self):
		from utils import CRC16
		from datamodel import DBGPSBinBackup, DBSystem, DBGPSBin
		from local import fromUTC
		from datetime import date, datetime, timedelta

		imei = self.request.get('imei')
		system = DBSystem.get_by_imei(imei)

		#if system is None

		cmd = self.request.get('cmd')
		total = 0
		if cmd:
			ukey = self.request.get('key')
			if cmd == 'getbin':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				bindata = db.get(db.Key(ukey))
				pdata = fix_bin(bindata.data)

				self.response.out.write(pdata)
				return
			elif cmd == 'fixcrc':
				bindata = db.get(db.Key(ukey))
				pdata = fix_bin(bindata.data)
				if pdata != bindata.data:
					bindata.data = pdata
					bindata.put()
				self.redirect("/binbackup?imei=%s" % imei)
				return
			elif cmd == 'fixlen':
				bindata = db.get(db.Key(ukey))
				pdata = bindata.data
				while (len(pdata) & 31)!=0: pdata += chr(0)
					
				crc = 0
				for byte in pdata:
					crc = CRC16(crc, ord(byte))
				pdata += chr(crc & 0xFF)
				pdata += chr((crc>>8) & 0xFF)
				bindata.data = pdata
				bindata.put()
				self.redirect("/binbackup?imei=%s" % imei)
				return
			elif cmd == 'del':
				db.delete(db.Key(ukey))
				self.redirect("/binbackup?imei=%s" % imei)
				return
			elif cmd == 'delall':
				dbbindata = DBGPSBinBackup.all(keys_only=True).order('cdate').ancestor(system).fetch(500)
				if dbbindata:
					db.delete(dbbindata)
				self.redirect("/binbackup?imei=%s" % imei)
				return
			elif cmd == 'delold':
				dbbindata = DBGPSBinBackup.all(keys_only=True).filter("cdate <=", datetime.now()-timedelta(days=30)).order('cdate').fetch(500)
				if dbbindata:
					db.delete(dbbindata)
				self.redirect("/binbackup")
				return
			elif cmd == 'pack':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				pdata = ''
				cfilter = self.request.get('filter')
				cnt = self.request.get('cnt')
				count = 500
				if cnt: count = int(cnt)
				today = date.today()
				aftercdate = self.request.get('after')
				asc = self.request.get('asc', 'None')

				if cfilter:
					dbbindata = DBGPSBinBackup.all().filter('cdate >=', today).order('-cdate').ancestor(system).fetch(count)
				else:
					if aftercdate and aftercdate!="None":
						if asc == 'yes':
							dbbindata = DBGPSBinBackup.all().filter("cdate >", datetime.strptime(aftercdate, "%Y%m%d%H%M%S") + timedelta(seconds = 1)).order('cdate').ancestor(system).fetch(count)
						else:
							dbbindata = DBGPSBinBackup.all().filter("cdate >", datetime.strptime(aftercdate, "%Y%m%d%H%M%S") + timedelta(seconds = 1)).order('-cdate').ancestor(system).fetch(count)
					else:
						if asc == 'yes':
							dbbindata = DBGPSBinBackup.all().order('cdate').ancestor(system).fetch(count)
						else:
							dbbindata = DBGPSBinBackup.all().order('-cdate').ancestor(system).fetch(count)

				for bindata in dbbindata:
					if bindata.crcok:
						npdata = bindata.data
						#bindata.datasize = len(npdata)
						if npdata[0] == 'P':	# POST-bug
							continue

						if (len(npdata) & 31)==0:
							pdata += npdata
						else:
							if ((len(npdata)-2) & 31) == 0:
								pdata += npdata[:-2]
							else:
								while (len(npdata) & 31)!=0: npdata += chr(0)
								pdata += npdata

				logging.info("Packets: %d" % len(dbbindata))
				if len(pdata) == 0:
					self.response.headers["BinData"] = "None"
					return

				self.response.headers["BinData"] = "Present"
				crc = 0
				for byte in pdata:
					crc = CRC16(crc, ord(byte))
				pdata += chr(crc & 0xFF)
				pdata += chr((crc>>8) & 0xFF)
				"""
				crc = ord(pdata[-1])*256 + ord(pdata[-2])
				pdata = pdata[:-2]
				_log += '\n==\tData size: %d' % len(pdata)

				"""

				if len(dbbindata) > 0:
					if asc == 'yes':
						self.response.headers["lastcdate"] = "%s" % dbbindata[-1].cdate.strftime("%Y%m%d%H%M%S")
					else:
						self.response.headers["lastcdate"] = "%s" % dbbindata[0].cdate.strftime("%Y%m%d%H%M%S")

				self.response.out.write(pdata)
				return
			elif cmd == 'parce':
				bindata = db.get(db.Key(ukey))
				pdata = bindata.data[:-2]
				#pdata = pdata[:-2]
				"""
				if ((len(pdata)-2) & 31) != 0:
					while (len(pdata) & 31)!=0:
						pdata += chr(0)
				if (len(pdata) & 31)==0:
					crc = 0
					for byte in pdata:
						crc = CRC16(crc, ord(byte))
					pdata += chr(crc & 0xFF)
					pdata += chr((crc>>8) & 0xFF)
				"""
				dataid = 0

				newbin = DBGPSBin(parent = system)
				newbin.dataid = dataid
				newbin.data = pdata #db.Text(pdata)
				newbin.put()

				url = "/bingps/parse?dataid=%s&key=%s" % (dataid, newbin.key())
				#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
				countdown=0
				taskqueue.add(url = url, method="GET", countdown=countdown)

				cursor = self.request.get('cursor')
				if cursor:
					self.redirect("/binbackup?imei=%s&cursor=%s" % (imei, cursor))
				else:
					self.redirect("/binbackup?imei=%s" % imei)

		if system:
			q = DBGPSBinBackup.all().order('-cdate').ancestor(system)

			cursor = self.request.get('cursor')
			if cursor:
				q.with_cursor(cursor)

			dbbindata = q.fetch(100)

			for bindata in dbbindata:
				bindata.datasize = len(bindata.data)
				if (bindata.datasize & 31)==0:
					bindata.needfix = True
					bindata.wronglen = False
					total += bindata.datasize
				else:
					bindata.needfix = False
					total += bindata.datasize - 2

					if ((bindata.datasize-2) & 31)!=0:
						bindata.wronglen = True
					else:
						bindata.wronglen = False

				if bindata.data[0] == 'P':
					bindata.postbug = True
				else:
					bindata.postbug = False

				bindata.sdate = fromUTC(bindata.cdate)	#.strftime("%d/%m/%Y %H:%M:%S")
			total += 2
			allusers = None

			self.response.headers['Content-Type'] = 'text/html'
			self.write_template({
				'imei': imei,
				'dbbindata': dbbindata,
				'cursor': cursor,
				'ncursor': q.cursor(),
				'total': total,
				'system': system,
				'allusers': allusers
			})
			return

		else:
			dbbindata = None
			allusers = DBSystem.all().fetch(500)
			qoldest = DBGPSBinBackup.all().order('cdate').fetch(1)
			if qoldest:
				oldest = fromUTC(qoldest[0].cdate)
			else:
				oldest = u"нет записей"
			coldest = DBGPSBinBackup.all(keys_only=True).filter("cdate <=", datetime.now()-timedelta(days=30)).order('cdate').count()

		#template_values = {}
		#template_values['imei'] = uimei
		#template_values['dbbindata'] = dbbindata

		self.response.headers['Content-Type'] = 'text/html'
		#path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template({
			'imei': imei,
			'dbbindata': dbbindata,
			'total': total,
			'system': system,
			'allusers': allusers,
			'oldest': oldest,
			'coldest': coldest,
		})


# обновление программного обеспечения
class Firmware(TemplatedPage):
	def get(self):
		from datamodel import DBFirmware
		from utils import CRC16
		#user = users.get_current_user()
		#username = ''
		#if user:
		#	username = user.nickname()
		#
		cmd = self.request.get('cmd')
		fid = self.request.get('id')
		swid = self.request.get('swid')
		hwid = self.request.get('hwid')
		boot = self.request.get('boot')
		if boot:
			if boot == 'yes':
				boot = True
			else:
				boot = False
		else:
			boot = False

		if cmd:
			if cmd == 'del':
				if fid:
					datamodel.DBFirmware().get_by_key_name(fid).delete()
				self.redirect("/firmware")

			elif cmd == 'check':	# Запросить версию самой свежей прошивки
				self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
					
				fw = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				if fw:
					self.response.out.write("SWID: %04X\r\n" % fw[0].swid)
				else:
					self.response.out.write("NOT FOUND\r\n")

			elif cmd == 'getbin':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				if fid:
					fw = DBFirmware.get_by_key_name(fid)
					fw = [fw]
				elif swid:
					fw = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				if fw:
					self.response.out.write(fw[0].data)
				else:
					self.response.out.write('NOT FOUND\r\n')

			elif cmd == 'get':
				if fid:
					fw = DBFirmware.get_by_key_name(fid)
					fw = [fw]
				elif swid:
					fw = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)

				self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
				if fw:
					by = 0
					line = 0
					crc2 = 0
					self.response.out.write("SWID:%04X" % fw[0].swid)
					self.response.out.write("\r\nLENGTH:%04X" % len(fw[0].data))

					for byte in fw[0].data:
						if by == 0:
							self.response.out.write("\r\nLINE%04X:" % line)
							line = line + 1
							by = 32
						self.response.out.write("%02X" % ord(byte))
						crc2 = CRC16(crc2, ord(byte))
						by = by - 1
					self.response.out.write("\r\n")
					self.response.out.write("CRC:%04X\r\n" % crc2)
					self.response.out.write("ENDDATA\r\n")
				else:
					self.response.out.write('NOT FOUND\r\n')

			elif cmd == 'patch':
				fws = DBFirmware.all().fetch(500)
				for fw in fws:
					if fw.boot:
						pass
					else:
						fw.boot = False
						fw.put()
				self.redirect("/firmware")
			else:
				self.redirect("/firmware")
		else:
			template_values = {}

			if hwid:
				firmwares = DBFirmware.all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).fetch(500)
			else:
				firmwares = DBFirmware.all().filter('boot =', boot).fetch(100)
			nfw = []
			for fw in firmwares:
				nfw.append({
					'key': fw.key().name(),
					'hwid': "%04X" % fw.hwid,
					'swid': "%04X" % fw.swid,
					'cdate': fw.cdate,
					'size': fw.size,
					'desc': fw.desc,
				})
			template_values['firmwares'] = nfw
			self.write_template(template_values)

	def post(self):
		from datamodel import DBFirmware
		self.response.headers['Content-Type'] = 'text/plain'

		boot = self.request.get('boot')

		pdata = self.request.body
		hwid = int(self.request.get('hwid'), 16)
		swid = int(self.request.get('swid'), 16)

		if boot:
			newfw = DBFirmware(key_name = "FWBOOT%04X" % hwid, desc = u"Загрузчик", boot = True)
		else:
			newfw = DBFirmware(key_name = "FWGPS%04X%04X" % (hwid, swid), desc = u"Образ ядра")
		newfw.hwid = hwid
		newfw.swid = swid
		newfw.data = pdata
		newfw.size = len(pdata)
		newfw.put()

		self.response.out.write("ROM ADDED: %d\r\n" % len(pdata))


application = webapp.WSGIApplication(
	[('/', MainPage),
		('/s/.*', StaticPage),
		('/addlog', AddLog),	# Событие, не требующее точной привязки ко времени
		('/config.*', Config),	# Конфигурация системы
		('/params.*', Params),	# Запрос параметров системы, например localhost/params?cmd=check&imei=353358019726996
		('/binbackup.*', BinBackup),
		('/firmware.*', Firmware),
	],
	debug=True
)

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
