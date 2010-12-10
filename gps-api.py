# -*- coding: utf-8 -*-
import logging

from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#from template import TemplatedPage
from datamodel import DBAccounts, DBSystem, DBGeo

from datetime import datetime, timedelta

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


class Debug_jqGrid(webapp.RequestHandler):
	def get(self):
		g_rows = int(self.request.get("rows", "1"))
		g_page = int(self.request.get("page", "1"))
		#g_sort = self.request.get("sidx", "dt"))
		#g_sort_order = self.request.get("sord", "asc"))
		g_search = self.request.get("_search", "false")
		g_nd = long(self.request.get("nd", "0"))
		
		rows = [];
		for i in xrange(g_rows):
			rows.append({
				"id": i,
				"cell": [
					datetime.utcnow().strftime("%Y-%b-%d  %H:%M:%S GMT"),	# dt
					i+(g_page-1)*g_rows,	# la
					i+1,			# lo
					i+2,			# sp
				],
			})
		jsonresp = {
			"page": g_page,
			"total": 1000,
			"record": 13,
			"records": 12269,
			"rows": rows,
			"userdata": {
				"tamount": 100,
				"ttax": 200,
				"ttotal": 300,
			}
		}
		
		self.response.out.write(json.dumps(jsonresp) + "\r")

# TBD!!! В этой процедуре утечка памяти!!! И очень быстрая
# Отказ от json не помогает

class GetGeo(webapp.RequestHandler):
	def get(self):
		skey = self.request.get("skey")
		if skey:
			system_key = db.Key(skey)

		recs = DBGeo.all().ancestor(system_key).order("date").fetch(100)

		g_rows = int(self.request.get("rows", "1"))
		g_page = int(self.request.get("page", "1"))
		#logging.info(g_rows)


		total = 0
		skip = (g_page-1) * g_rows
		isid = skip
		goted = 0

		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		#rows = [];					# json
		self.response.out.write('{"rows":[\n ')		# ! json

		first = True

		for rec in recs:
			#bdate = datetime(rec.date.

			"""
			# Сортируем список timelist
			# Правильнее делать это на этапе получений точки! TBD!!!
			sindex = sorted([(item, index) for index, item in enumerate(rec.timelist)])
			"""
			lsindex = rec.count
			#logging.info("\n==  Before: %s\n== After: %s" % (repr(rec.timelist), repr(sindex)))

			for p in xrange(lsindex):
				total = total + 1

				# json
				#if len(rows) >= g_rows: continue

				# !json
				if goted >= g_rows: continue

				if skip > 0:
					skip = skip - 1
					continue

				#p = sindex[i][1]	# Получаем индекс из отсортированого списка

				# Если бы не необходимость пропускать значения, то можно было бы воспользоваться
				# итератором
				#  for u in rec.get_all():

				goted += 1
				r = rec.get_item(p)

				# json
				"""
				rows.append({
					"id": isid,
					"cell": [
						r['time'].strftime("%Y-%m-%d %H:%M:%S"),	# dt
						#ptime.strftime("%Y-%m-%d"),	# dt
						r['lat'],
						r['lon'],
						r['sats'],
						r['speed'],
						r['cource'],
						r['vout'],
						r['vin'],
						r['fsource'],
						#rec.extend[p]
						"%d" % total
					],
				})
				"""

				# ! json
				if first:
					first = False
				else:
					self.response.out.write(',\n ')
				self.response.out.write('{"id": %d, "cell": ["%s", %f, %f, %d, %f, %f, %f, %f, %d, "%s"]}' % (
					isid,
					r['time'].strftime("%Y-%m-%d %H:%M:%S"),	# dt
					#ptime.strftime("%Y-%m-%d"),	# dt
					r['lat'],
					r['lon'],
					r['sats'],
					r['speed'],
					r['cource'],
					r['vout'],
					r['vin'],
					r['fsource'],
					#rec.extend[p]
					str(total)
				))

				isid = isid + 1

		# json
		"""
		jsonresp = {
			"page": g_page,
			"total": int((total + g_rows - 1) / g_rows),
			"record": 13,
			"records": total,
			"rows": rows,
			"userdata": {
				"tamount": 1000,
				"g_rows": g_rows,
				"hours": len(recs),
				"total": total,
				"goted": len(rows),
			}
		}
		"""

		# ! json
		self.response.out.write('\n],\n "page": %d, "total": %d, "record": %d, "records": %d,\n "userdata": {"tamount": %d, "g_rows": %d, "hours": %d, "total": %d, "goted": %d}}' % (
			g_page,
			int((total + g_rows - 1) / g_rows),
			13,
			total,
			1000,
			g_rows,
			len(recs),
			total,
			goted
		))

		# json
		#self.response.out.write(json.dumps(jsonresp) + "\r")
		#rows = None
		#jsonresp = None


# Поиск места в сортированом списке для вставки нового значения (метор половинного деления)
def find_index(arr, value):
	s = 0
	e = len(arr) - 1
	if e == -1:
		return 0

	while (s+1) < e:
		m = (s+e) / 2
		if arr[m] > value:
			e = m
		else:
			s = m

	if arr[s] > value:
		return s
	else:
		if arr[e] < value:
			return e + 1
		else:
			return e

class PointWorker(object):
	def __init__(self, skey):
		#logging.info('PointWorker: __init__(%s)' % str(skey))
		self.last_pkey = None
		self.rec = None
		self.rec_changed = False
		self.system_key = skey
		self.nrecs = 0

	def Add_point(self, ptime, lat, lon, sats, speed, cource, vout, vin, fsource):
		pkey = ptime.strftime("geo_%Y%m%d%H")
		#logging.info('PointWorker: Add_point(%s)' % str(ptime))
		if pkey != self.last_pkey:
			if self.last_pkey is not None:
				self.Flush()
			self.last_pkey = pkey
			self.rec = DBGeo.get_by_key_name(pkey, parent=self.system_key)
			if self.rec is None:
				self.rec = DBGeo(
					parent = self.system_key,
					key_name = pkey,
					date = datetime(ptime.year, ptime.month, ptime.day, ptime.hour, 0, 0)
				)
				self.nrecs = 0
			else:
				self.nrecs = self.rec.count

		timep = ptime.minute * 60 + ptime.second

		change = self.rec.add_point({
			'time': timep,
			'lat': lat,
			'lon': lon,
			'sats': sats,
			'speed': speed,
			'cource': cource,
			'vout': vout,
			'vin': vin,
			'fsource': fsource
		})
		if change:
			self.nrecs += 1
			self.rec_changed = True
		"""
		if timep not in self.rec.timelist():
			nindex = self.rec.find_pos(timep)	# find_index(self.rec.timelist(), timep)

			self.rec.timelist.insert(nindex, timep)
			self.rec.geolist.insert(nindex, db.GeoPt(lat, lon))
			self.rec.sats.insert(nindex, sats)
			self.rec.speed.insert(nindex, speed)
			self.rec.course.insert(nindex, cource)
			self.rec.vout.insert(nindex, vout)
			self.rec.vin.insert(nindex, vin)
			self.rec.fsource.insert(nindex, fsource)
			self.rec.extend.insert(nindex, u"")

			self.nrecs += 1
			self.rec_changed = True

			#rec.put()
		"""

	def Flush(self):
		#logging.info('PointWorker: Flush (%d recs)' % self.nrecs)
		if (self.rec is not None) and self.rec_changed:
			self.rec.put()
		self.rec = None
		self.rec_changed = False
		self.nrecs = 0
		


def put_random_point(worker):
	import random
	# Подготовим точку
	#datetime.utcnow()
	#ptime = datetime.today() + timedelta(seconds = random.randint(0, 86400-1))
	ptime = datetime.today() + timedelta(seconds = random.randint(0, 3600-1))
	lat = random.uniform(-90.0, 90.0)
	lon = random.uniform(-180.0,180.0)
	sats = random.randint(0,255)
	speed = random.uniform(0.0, 260.0)
	cource = random.uniform(0.0, 360.0)
	vout = random.uniform(0.0, 36.0)
	vin = random.uniform(0.0, 6.0)
	fsource = random.randint(0, 255)

	worker.Add_point(ptime, lat, lon, sats, speed, cource, vout, vin, fsource)

def put_seq_point(worker, start, offset):
	import random
	# Подготовим точку
	#datetime.utcnow()
	#ptime = datetime.today() + timedelta(seconds = random.randint(0, 86400-1))
	ptime = start + timedelta(seconds = offset)
	lat = random.uniform(-90.0, 90.0)
	lon = random.uniform(-180.0,180.0)
	sats = random.randint(0,255)
	speed = random.uniform(0.0, 260.0)
	cource = random.uniform(0.0, 360.0)
	vout = random.uniform(0.0, 36.0)
	vin = random.uniform(0.0, 6.0)
	fsource = random.randint(0, 255)

	worker.Add_point(ptime, lat, lon, sats, speed, cource, vout, vin, fsource)


class DebugGeo(webapp.RequestHandler):
	def post(self):
		import random

		skey = self.request.get("skey")
		if skey:
			system_key = db.Key(skey)
		else:
			self.response.out.write("ERROR: not a skey.")
			return

		g_cnt = int(self.request.get("cnt", "1"))

		worker = PointWorker(system_key)

		#for i in xrange(g_cnt):
		#	put_random_point(worker)

		start = datetime.today() + timedelta(seconds = random.randint(0, 86400-1))

		for i in xrange(g_cnt):
			put_seq_point(worker, start, i)

		worker.Flush()

		self.response.out.write("OK")

class Geo_Del(webapp.RequestHandler):
	def post(self):
		self.response.out.write(u"Не реализовано")


application = webapp.WSGIApplication(
	[
	('/api/info.*', Info),
	('/api/version.*', Version),
	('/api/debug_jqGrid.*', Debug_jqGrid),
	('/api/get_geo.*', GetGeo),
	('/api/geo/del.*', Geo_Del),
	('/api/debug_geo.*', DebugGeo),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
