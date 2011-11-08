# -*- coding: utf-8 -*-

import os
import logging
#import datamodel
#import utils

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue
#from google.appengine.api import taskqueue
from google.appengine.api import urlfetch

from datamodel import DBSystem, DBGeo, PointWorker, DBGPSBin, DBGPSBinBackup

from datetime import date, timedelta, datetime

from utils import CRC16
import updater

from google.appengine.api import memcache


SERVER_NAME = os.environ['SERVER_NAME']
os.environ['CONTENT_TYPE'] = "application/octet-stream"

jit_lat = 0
jit_long = 0

USE_BACKUP = False

def SaveGPSPointFromBin(pdata, result):
	def LogError():
		sstr = "==  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		#sstr += "\nEncode partial data:\n\tdate:%s\n\tLatitude:%f\n\tLongitude:%f\n\tSatelites:%d\n\tSpeed:%f\n\tCource:%f\n\tAltitude:%f" % (datestamp, latitude, longitude, sats, speed, course, altitude)
		logging.error( sstr )

	global jit_lat
	global jit_long

	if ord(pdata[0]) != 0xF2:	# ID
		logging.error("\n==\t GPS_PARSE_ERROR: ID != 0xF2")
		return None
	if ord(pdata[1]) != 0x20:
		logging.error("\n==\t GPS_PARSE_ERROR: LENGTH != 0x20")
		return None	# LENGTH

	day = ord(pdata[2])
	month = ord(pdata[3]) & 0x0F
	year = (ord(pdata[3]) & 0xF0)/16 + 2010
	hours = ord(pdata[4])
	minutes = ord(pdata[5])
	seconds = ord(pdata[6])

	"""
	if day<1 or day>31:
		logging.error("\n==\t GPS_PARSE_ERROR: DAY=%d" % day)
		return None	# LENGTH
	if month<1 or month>12:
		logging.error("\n==\t GPS_PARSE_ERROR: MONTH=%d" % month)
		return None	# LENGTH
	if year<2010 or year>2014:
		logging.error("\n==\t GPS_PARSE_ERROR: YEAR=%d" % year)
		return None	# LENGTH
	"""

	try:
		datestamp = datetime(year, month, day, hours, minutes, seconds)
	except ValueError, strerror:
		logging.error("\n==\t GPS_PARSE_ERROR: error datetime (%s)" % strerror)
		LogError()
		return None	# LENGTH

	if datestamp > datetime.now() + timedelta(days=1):
		logging.error("\n==\t GPS_PARSE_ERROR: error datetime: future point")
		return None

	latitude = float(ord(pdata[7])) + (float(ord(pdata[8])) + float(ord(pdata[9])*100 + ord(pdata[10]))/10000.0)/60.0
	longitude = float(ord(pdata[11])) + (float(ord(pdata[12])) + float(ord(pdata[13])*100 + ord(pdata[14]))/10000.0)/60.0
	if ord(pdata[15]) & 1:
		latitude = - latitude
	if ord(pdata[15]) & 2:
		longitude = - longitude

	sats = ord(pdata[16])

	fix = 1
	speed = (float(ord(pdata[17])) + float(ord(pdata[18])) / 100.0) * 1.852 # Переведем в км/ч

	if ord(pdata[15]) & 4:
		course = float(ord(pdata[19])*2 + 1) + float(ord(pdata[20])) / 100.0
	else:
		course = float(ord(pdata[19])*2) + float(ord(pdata[20])) / 100.0;

	altitude = 0.0	#100.0 * float(ord(pdata[21]) + ord(pdata[22])) / 10.0;

	error = False

	if latitude > 90.0: error = True
	if latitude < -90.0: error = True
	if longitude > 180.0: error = True
	if longitude < -180.0: error = True

	if SERVER_NAME=='localhost':
		#jit_lat = jit_lat + (random.random()-0.5)*0.001
		#jit_long = jit_long + (random.random()-0.5)*0.001
		#latitude = latitude + jit_lat
		#longitude = longitude + jit_long
		pass

	if error:
		logging.error("Corrupt latitude or longitude %f, %f" % (latitude, longitude))
		LogError()
		"""
		sstr = "  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		sstr += "\nEncode partial data:\n\tdate:%s\n\tLatitude:%f\n\tLongitude:%f\n\tSatelites:%d\n\tSpeed:%f\n\tCource:%f\n\tAltitude:%f" % (datestamp, latitude, longitude, sats, speed, course, altitude)
		logging.error( sstr )
		"""
		return None

	if sats < 3:
		logging.error("No sats.")
		LogError()
		return None

	#in1 = float(self.request.get('in1'))*100.0/65535 
	#in2 = float(self.request.get('in2'))*100.0/65535 
	in1 = 0.0
	in2 = 0.0
	if (ord(pdata[23]) == 0) and (ord(pdata[24]) == 0):
		vout = float(ord(pdata[21])) / 10.0
		vin = float(ord(pdata[22])) / 50.0
	else:
		vout = float(ord(pdata[21]) + 256*ord(pdata[22])) / 100.0
		vin = float(ord(pdata[23]) + 256*ord(pdata[24])) / 100.0

	fsource = ord(pdata[26]);	# Причина фиксации координаты

	#_log += '\n Date: %s' % datestamp.strftime("%d/%m/%Y %H:%M:%S")
	#_log += '\n Latitude: %.5f' % latitude
	#_log += '\n Longitude: %.5f' % longitude
	#_log += '\n Satelits: %d' % sats
	#_log += '\n Speed: %.5f' % speed
	#_log += '\n Course: %.5f' % course
	#_log += '\n Altitude: %.5f' % altitude
	#logging.info('[%s]' % datestamp.strftime("%d/%m/%Y %H:%M:%S"))

	#gpspoint = datamodel.DBGPSPoint()
	"""
	gpspoint = datamodel.DBGPSPoint(key_name = "gps_%s_%s" % (result.user.imei, datestamp.strftime("%Y%m%d%H%M%S")))
	#gpspoint = datamodel.DBGPSPoint()
	gpspoint.user = result.user
	gpspoint.date = datestamp
	gpspoint.latitude = latitude
	gpspoint.longitude = longitude
	gpspoint.sats = sats
	gpspoint.fix = fix
	gpspoint.speed = speed
	gpspoint.course = course
	gpspoint.altitude = altitude
	gpspoint.vout = vout
	gpspoint.vin = vin
	gpspoint.in1 = in1
	gpspoint.in2 = in2
	gpspoint.fsource = fsource
	"""

	"""
	from local import fromUTC

	point = {
		'time': '%s' % fromUTC(datestamp).strftime("%d/%m/%Y %H:%M:%S"),
		'lat': '%.4f' % latitude,
		'lon': '%.4f' % longitude,
	}
	LogError()
	logging.info('POINT: %s' % repr(point))
	"""

	return {
		'time': datestamp,
		'lat': latitude,
		'lon': longitude,
		'sats': sats,
		'speed': speed,
		'course': course,
		'vout': vout,
		'vin': vin,
		'fsource': fsource 
	}

class BinGpsParse(webapp.RequestHandler):
	def get(self):
		from geo import updateLasts
		from updater import inform

		#logging.info("Key: %s" % self.request.get('key'))
		#logging.info("Dataid: %s" % self.request.get('dataid'))
		#_log = '\n==\tEnviron: '
		#for k,v in os.environ.items():
		#	_log += "\n==\t%s = %s" % (str(k), str(v))
		#logging.info(_log)

		#logging.info('\n==\tRBody size: %d' % len(self.request.body))
		#logging.info('Body: %s' % self.request.body)
		#return

		_log = "\n== BINGPS/PARSE ["

		pdata = None
		skey = None
		result = None
		key = db.Key(self.request.get('key'))

		value = memcache.get("newbi_%s" % key)
		if value is not None:
			skey, pdata = value
			_log += 'Cached data by memcache'
		else:
			_log += '!!! Fail caching data by memcache!'
			result = DBGPSBin.get(key)
			skey = result.parent().key()
			if result:
				pdata = result.data

		if pdata is not None:
			#dataid = result.dataid
			#pdata = result.data
			plen = len(pdata)
			#_log += '\n==\tDATA ID: %d' % dataid
			_log += '\n==\tDATA LENGHT: %d' % plen

			#_log += '\nParsing...'

			worker = PointWorker(skey)

			offset = 0
			points = 0
			lasttime = None

			while offset < plen:
				if pdata[offset] != '\xFF':
					offset += 1
					continue

				try:
					p_id = ord(pdata[offset+1])	# Идентификатор пакета
					p_len = ord(pdata[offset+2])	# Длина пакета в байтах

					if p_id == 0xF2:
						point = SaveGPSPointFromBin(pdata[offset+1:offset+1+32], result)
						if point:
							if (lasttime is not None) and (point['time'] < lasttime):
								_log += '\n Time must always grow or repeat - ignored'
							else:
								lasttime = point['time']
								worker.Add_point(point)
								points += 1
					else:
						_log += '\n Unknown id=%02X' % p_id
					offset += p_len
				except:
					_warn = '\n Error parce at %d offset' % offset
					_warn += '\n==\tpdata size: %d' % plen
					_warn += '\n==\tpdata: '
					for data in pdata:
						_warn += ' %02X' % ord(data)
					logging.warning(_warn)
					offset += 1

			worker.Flush()

			if points > 0:
				_log += '\n==\tSaved points: %d\n' % points

				updateLasts(skey);
				inform('geo_change', skey, {
					'points': points
				})

			else:
				logging.error("Packet has no data or data is corrupted.\n")

			if result is not None:
				result.delete()
			else:
				db.delete(key)

			#_log += '\nData deleted.\n'
			_log += '\nOk\n'
			
			self.response.out.write('BINGPS/PARSE: OK\r\n')
			
		else:
			self.response.out.write('BINGPS/PARSE: NODATA\r\n')

		logging.info(_log)

"""
_CHARSET_RE = re.compile(r';\s*charset=([^;\s]*)', re.I)
environ.get('CONTENT_TYPE', '')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

"""

#class BinGpsTask(webapp.RequestHandler):
#	def post(self):
#		logging.info('Bla,bla,bla')
#		self.response.out.write('OK\r\n')


class BinGps(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('OK\r\n')

	def post(self):
		from datamodel import DBNewConfig
		from inform import Informer
		from urllib import unquote_plus
		import os

		_log = "\n== BINGPS ["
		self.response.headers['Content-Type'] = 'application/octet-stream'
		imei = self.request.get('imei')
		#system = DBSystem.get_or_create(imei)
		skey = DBSystem.getkey_or_create(imei)

		sdataid = self.request.get('dataid')
		if sdataid:
			dataid = int(sdataid, 16)
		else:
			dataid = 0

		#_log += '\n==\tEnviron: '
		#for k,v in os.environ.items():
		#	_log += "\n==\t%s = %s" % (str(k), str(v))

		#_log += '\n==\tRBody size: %d' % len(self.request.body)
		#_log += '\n==\tRBody: '
		#for data in self.request.body:
		#	_log += ' %02X' % ord(data)

		pdata = ''
		if 'Content-Type' in self.request.headers:
			if self.request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
				pdata = unquote_plus(self.request.body)
			else:
				pdata = self.request.body

		#pdata = self.request.body

		for k,v in self.request.headers.items():
			_log += "\n==\tHeader: %s = %s" % (str(k), str(v))

		_log += '\n==\tData ID: %d' % dataid

		_log += '\n==\tBody size: %d' % len(pdata)
		"""
		_log += '\n==\tBody: '
		for data in pdata:
			_log += ' %02X' % ord(data)
		"""

		if USE_BACKUP:
			_log += '\nSaving to backup'
			newbinb = DBGPSBinBackup(parent = skey)
			newbinb.dataid = dataid
			newbinb.data = pdata

			crc = ord(pdata[-1])*256 + ord(pdata[-2])
			pdata = pdata[:-2]
			_log += '\n==\tData size: %d' % len(pdata)

			crc2 = 0
			for byte in pdata:
				crc2 = CRC16(crc2, ord(byte))

			if crc!=crc2:
				_log += '\n==\tWarning! Calculated CRC: 0x%04X but system say CRC: 0x%04X. (Now error ignored.)' % (crc2, crc)
				_log += '\n==\t\tData (HEX):'
				for data in pdata:
					_log += ' %02X' % ord(data)

				newbinb.crcok = False
				newbinb.put()
				logging.info(_log)
				self.response.out.write('BINGPS: CRCERROR\r\n')
				return
			else:
				_log += '\n==\tCRC OK %04X' % crc

			newbinb.crcok = True
			newbinb.put()

		newbin = DBGPSBin(parent = skey)
		newbin.dataid = dataid
		newbin.data = pdata #db.Text(pdata)
		newbin.put()

		#logging.info("==> Bin data: %s" % repr(pdata))
		#parts = pdata.split('\xFF')
		#logging.info("==> Parts data: %s" % repr(parts))

		_log += '\nSaved to DBGPSBin creating tasque'

		#url = "/bingps/parse?dataid=%s&key=%s" % (dataid, newbin.key())
		#url = "/bingps/parse"
		#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
		#countdown=0

		#logging.info("memcache_key: newbi_%s" % newbin.key())
		memcache.set("newbi_%s" % newbin.key(), (skey, pdata), time = 30)
		taskqueue.add(url='/bingps/parse', method="GET", params={'dataid': dataid, 'key':newbin.key()})
		#taskqueue.add(url='/bingps/parse', params={'key': newbin.key()})
		#taskqueue.add(url = '/bingps/task', params={'dataid': dataid, 'key':newbin.key()})
		#taskqueue.add(url = '/bingps/task')

		#newconfigs = utils.CheckUpdates(userdb)
		#if newconfigs:
		#	self.response.out.write('CONFIGUP\r\n')

		#infos = inform.get_by_imei(imei)
		#if infos:
		#	self.response.out.write(infos)

		for info in Informer.get_by_imei(imei):
			self.response.out.write(info + '\r\n')


		value = memcache.get("update_config_%s" % imei)
		if value is not None:
			if value == "no":
				pass
			elif value == "yes":
				self.response.out.write('CONFIGUP\r\n')
		else:
			newconfigs = DBNewConfig.get_by_imei(imei)
			newconfig = newconfigs.config
			if newconfig and (newconfig != {}):
				memcache.set("update_config_%s" % imei, "yes")
				self.response.out.write('CONFIGUP\r\n')
			else:
				memcache.set("update_config_%s" % imei, "no")

		self.response.out.write('BINGPS: OK\r\n')

		logging.info(_log)
		return

		#_log = "\nUrl-fetch redirect: "
		logging.info("\nUrl-fetch redirect: ")
		#url = "http://212.110.139.65/"
		#url = "http://gps-maps.appspot.com/gpstestbin?imei=%s" % uimei
		host = "gps-maps.appspot.com"	#http://gps-maps.appspot.com
		host = "74.125.39.141"	#http://gps-maps.appspot.com
		url = "http://%s/gpstestbin?imei=%s" % (host, uimei)
		#url = "http://localhost/gpstestbin?imei=%s" % uimei
		result = urlfetch.fetch(
			url,
			payload = pdata,
			method = urlfetch.POST,
			headers={'Content-Type': 'application/octet-stream'}
		)
		if result.status_code == 200:
			pass
			logging.info('Url fetch: Ok.')
		else:
			logging.info('Url fetch: Fail.')

application = webapp.WSGIApplication(
	[
#	('/bingps/task.*', BinGpsTask),
	('/bingps/parse.*', BinGpsParse),
	('/bingps.*', BinGps),
	],
	debug=True
)

def main():
	os.environ['CONTENT_TYPE'] = "application/octet-stream"
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
