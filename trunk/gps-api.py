# -*- coding: utf-8 -*-
#from gc import get_objects
import os
import gc
import logging

#from django.utils import simplejson as json
from repy import simplejson as json

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch

#from template import TemplatedPage
from datamodel import DBAccounts, DBSystem, DBGeo, PointWorker
import local
import geo
import updater

from datetime import datetime, timedelta

API_VERSION = 1.0
SERVER_NAME = os.environ['SERVER_NAME']
MAXPOINTS = 100000

logging.getLogger().setLevel(logging.DEBUG)

class BaseApi(webapp.RequestHandler):
	requred = ()
	def parcer(self):
		return {'answer': 'no', 'reason': 'base api'}

	def _parcer(self):
		if 'account' in self.requred:
			self.akey = self.request.get('akey', None)
			if self.akey is None:
				return {"answer": "no", "reason": "akey not defined or None"}

			try:
				self.account = DBAccounts.get(db.Key(self.akey))
			except db.datastore_errors.BadKeyError, e:
				return {'answer': 'no', 'reason': 'account key error', 'comments': '%s' % e}

			if self.account is None:
				return {'answer': 'no', 'reason': 'account not found'}

		if 'skey' in self.requred:
			skey = self.request.get("skey", None)
			logging.info(skey)
			if skey is None:
				return {'answer': 'no', 'reason': 'skey not defined or None'}
			try:
				self.skey = db.Key(skey)
			except db.datastore_errors.BadKeyError, e:
				return {'answer': 'no', 'reason': 'skey key error', 'comments': '%s' % e}

		if 'imei' in self.requred:
			self.imei = self.request.get('imei', None)
			if self.imei is None:
				return {'answer': 'no', 'result': 'imei not defined'}


		return self.parcer()

	def get(self):
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
		self.response.out.write(json.dumps(self._parcer(), indent=2) + "\r")

class Version(BaseApi):
	def parcer(self):
		return {'answer': 'ok', 'version': API_VERSION}

class Info(BaseApi):
	requred = ('account')
	def parcer(self, **argw):
		lsys = []
		for sys in self.account.systems:
			lsys.append({
				"key": str(sys.key()),
				"imei": sys.imei,
				"phone": sys.phone,
				"desc": sys.desc,
				"premium": sys.premium >= datetime.now(),
			})
		accinfos = {
			'key': "%s" % self.account.key(),
			'name': self.account.name,
			'user': {
				'email': self.account.user.email(),
				'id': self.account.user.user_id(),
			},
			'systems': lsys,
		}

		#sysinfos = []
		#systems = DBSystem.all(keys_only=True).fetch(1000)
		#for rec in systems:
		#	sysinfos.append({'imei': rec.name()[4:], 'key': "%s" % rec, })

		return {
			'answer': 'ok',
			'info': {
				'account': accinfos,
				#'systems': sysinfos,
			}
		}
		

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
						r['course'],
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
					local.fromUTC(r['time']).strftime("%Y-%m-%d %H:%M:%S"),	# dt
					#ptime.strftime("%Y-%m-%d"),	# dt
					r['lat'],
					r['lon'],
					r['sats'],
					r['speed'],
					r['course'],
					r['vout'],
					r['vin'],
					r['fsource'],
					r['fsourcestr'],
					#rec.extend[p]
					#str(total)
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
	course = random.uniform(0.0, 360.0)
	vout = random.uniform(0.0, 36.0)
	vin = random.uniform(0.0, 6.0)
	fsource = random.randint(0, 255)

	#worker.Add_point(ptime, lat, lon, sats, speed, course, vout, vin, fsource)
	worker.Add_point({
		'time': ptime,
		'lat': lat,
		'lon': lon,
		'sats': sats,
		'speed': speed,
		'course': course,
		'vout': vout,
		'vin': vin,
		'fsource': fsource
	})

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
	course = random.uniform(0.0, 360.0)
	vout = random.uniform(0.0, 36.0)
	vin = random.uniform(0.0, 6.0)
	fsource = random.randint(0, 255)

	worker.Add_point({
		'time': ptime,
		'lat': lat,
		'lon': lon,
		'sats': sats,
		'speed': speed,
		'course': course,
		'vout': vout,
		'vin': vin,
		'fsource': fsource
	})


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

		for i in xrange(g_cnt):
			put_random_point(worker)

		"""
		start = datetime.today() + timedelta(seconds = random.randint(0, 86400-1))

		for i in xrange(g_cnt):
			put_seq_point(worker, start, i)
		"""

		#worker.Flush()
		del worker

		self.response.out.write("OK")

class Geo_Del(BaseApi):
	requred = ('imei')
	def parcer(self, **argw):

		logging.info('API: /api/geo/del');

		system = DBSystem.get_by_imei(self.imei)
		if system is None:
			logging.info('API: /api/geo/del: no sys');
			return {
				'answer': 'error',
				'result': 'system not found (IMEI:%s)' % self.imei,
			}

		if self.request.get('task', '') == 'yes':
			logging.info('API: /api/geo/del: call task');
			dtto = local.toUTC(datetime.strptime(self.request.get("to"), "%y%m%d%H%M%S"))
			qu = DBGeo.all(keys_only=True).filter('date <', dtto).order('date').ancestor(system).fetch(200)
			db.delete(qu)

			logging.info('API: /api/geo/del: delete %d records' % len(qu));

			#return {'answer': 'ok', 'result': 'End Task'}

			if len(qu) < 200:
				logging.info('API: /api/geo/del: finish task');
				return {
					'answer': 'ok',
					'result': 'continue task for delete',
					'dateto': str(dtto),
					'count': len(qu)
				}

		logging.info('API: /api/geo/del: create task');
		url = "/api/geo/del?task=yes&imei=%s&to=%s" % (self.imei, self.request.get('to',''))
		countdown=0
		taskqueue.add(url = url, method="GET", countdown=countdown)

		return {
			'answer': 'ok',
			'result': 'add task for delete',
		}

class Geo_GetO(webapp.RequestHandler):
	def get(self):
		from math import log

		"""
		prof = "gc START: %s\n" % dir(gc)
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		logging.info(prof)
		"""

		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		skey = self.request.get("skey")
		if skey is None:
			self.response.out.write(json.dumps({'answer': None}) + "\r")
			return

		system_key = db.Key(skey)

		#pfrom = self.request.get("from")
		dtfrom = local.toUTC(datetime.strptime(self.request.get("from"), "%y%m%d%H%M%S"))
		dhfrom = datetime(dtfrom.year, dtfrom.month, dtfrom.day, dtfrom.hour & ~7, 0, 0)

		dtto = local.toUTC(datetime.strptime(self.request.get("to"), "%y%m%d%H%M%S"))
		dhto = datetime(dtto.year, dtto.month, dtto.day, dtto.hour & ~7, 0, 0)

		pto = self.request.get("to")

		recs = DBGeo.all().ancestor(system_key).filter("date >=", dhfrom).filter("date <=", dhto).order("date")#.fetch(1000)
		points = []
		l_lat = []	# Список индексов (lat, index)
		l_lon = []	# Список индексов (lon, index)
		counts = []
		stops = []
		plat = 0.0
		plon = 0.0

		DS = 0.8
		MS = DS/(2**20)

		pl = 0
		b_lat_l = 90.0
		b_lon_l = 180.0
		b_lat_r = -90.0
		b_lon_r = -180.0

		maxp = 10000		# На данный момент ограничение 10тыс точек
		ind = 0 

		stop_start = None

		for rec in recs:
			logging.info('==> API:GEO:GET  fetch DBGeo[%s]' % rec.key().name())
			if maxp == 0: break
			else: maxp -= 1

			counts.append(rec.count)
			#c = rec.count
			#for i in xrange(c):
			#	point = rec.get_item(i)
			for point in rec.get_all():
				if point['time'] < dtfrom:	# Это не очень оптимально, нужно заменить поиском
					continue
				if point['time'] > dtto:	# Это не очень оптимально, нужно заменить поиском
					break

				if maxp == 0: break
				else: maxp -= 1

				d = max(MS, max(abs(plat - point['lat']), abs(plon - point['lon'])))
				plat = point['lat']
				plon = point['lon']
				
				points.append([
					#local.toUTC(point['time']).strftime("%d/%m/%Y %H:%M:%S"),
					local.fromUTC(point['time']).strftime("%y%m%d%H%M%S"),
					plat, #point['lat'],
					plon, #point['lon'],
					int(point['course']),
					#20,
					int(round(log(DS/d, 2), 0)),
				])
				l_lat.append((plat, ind))
				#l_lon.append((plon, ind))

				#if point['speed'] < 1.0:

				if point['fsource'] in (2, 3, 7):
					if stop_start is None:
						stop_start = {}
						stop_start['ind'] = ind
						stop_start['lat'] = plat
						stop_start['lon'] = plon
				if point['fsource'] == 6:
					if stop_start is not None:
						stops.append({
							'i': stop_start['ind'],
							'p': (stop_start['lat'], stop_start['lon']),
							's': ind,
						})
						stop_start = None
				"""
				if point['fsource'] in (2, 3, 7):
					if stop_start is None:
						stop_start = {}
						stop_start['ind'] = ind
						stop_start['lat'] = plat
						stop_start['lon'] = plon
						stops.append({'i': ind, 'p': (plat, plon)})
					else:
						if stop_start['lat'] != plat or stop_start['lon'] != plon:
							stop_start['ind'] = ind
							stop_start['lat'] = plat
							stop_start['lon'] = plon
							stops.append({'i': ind, 'p': (plat, plon)})
				"""


				b_lat_l = min(b_lat_l, plat)
				b_lon_l = min(b_lon_l, plon)
				b_lat_r = max(b_lat_r, plat)
				b_lon_r = max(b_lon_r, plon)

				ind += 1

		# Zoom для первой и последней точки наивысший (отображать всегда)
		plen = len(points) 
		if plen>0:
			points[0][-1] = 0
			points[-1][-1] = 0

		# Вычислим subbounds (TBD)
		
		# Разобьем на 8 частей по lat
		l_lat.sort()
		#l_lon.sort()
		subbounds = []
		for i in range(8):
			l_lon = []
			i1 = plen * i // 8
			i2 = plen * (i+1) // 8
			#logging.info('i1 = %s' % str(i1))
			#logging.info('i2 = %s' % str(i2))
			for i3 in xrange(i1, i2):
				l_lon.append((points[l_lat[i3][1]][2], l_lat[i3][1]))
			l_lon.sort()
			for j in range(8):
				sbl = []
				j1 = len(l_lon) * j // 8
				j2 = len(l_lon) * (j+1) // 8
				#logging.info(' j1 = %s' % str(j1))
				#logging.info(' j2 = %s' % str(j2))
				nmin_lat = 180
				nmax_lat = -180
				for j3 in xrange(j1, j2):
					nmin_lat = min(nmin_lat, points[l_lon[j3][1]][1])
					nmax_lat = max(nmax_lat, points[l_lon[j3][1]][1])
					sbl.append(l_lon[j3][1])
				if(len(sbl)):
					subbounds.append({
						#'sw': (l_lat[i1][0], l_lon[j1][0]),
						#'ne': (l_lat[i2-1][0], l_lon[j2-1][0]),
						'sw': (nmin_lat, l_lon[j1][0]),
						'ne': (nmax_lat, l_lon[j2-1][0]),
						'i': sbl,
					})
				
		#subbounds.append(((b_lat_l, b_lon_l), ((b_lat_l+b_lat_r)/2, (b_lon_l+b_lon_r)/2)))

		jsonresp = {
			'answer': 'ok',
			#'bcount': len(recs),
			'count': len(points),
			#'counts': counts,
			'format': ["date", "lat", "lon", "course", "minzoom"],
			'points': points,
			'stops': stops,
			'bounds': {'sw': (b_lat_l, b_lon_l), 'ne': (b_lat_r, b_lon_r)},
			'subbounds': subbounds,
			#'slat': l_lat,
			#'slon': l_lon,
		}
		self.response.out.write(json.dumps(jsonresp, separators=(',',':')) + "\r")

		"""
		prof = "gc AFTER:\n"
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		logging.info(prof)

		gc.collect()

		prof = "gc COLLECT:\n"
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		#prof += "gc.get_objects()=%s\n" % repr(gc.get_objects())
		logging.info(prof)
		"""

class Geo_Get(BaseApi):
	requred = ('skey')
	def parcer(self):
		from math import log, sqrt

		"""
		prof = "gc START: %s\n" % dir(gc)
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		logging.info(prof)
		"""


		#pfrom = self.request.get("from")
		dtfrom = local.toUTC(datetime.strptime(self.request.get("from"), "%y%m%d%H%M%S"))

		dtto = local.toUTC(datetime.strptime(self.request.get("to"), "%y%m%d%H%M%S"))

		options = self.request.get('options', '').split(',')
		logging.info('options=%s' % repr(options))

		points = []
		l_lat = []	# Список индексов (lat, index)
		l_lon = []	# Список индексов (lon, index)
		counts = []
		stops = []
		plat = 0.0
		plon = 0.0

		DS = 0.8
		MS = DS/(2**20)

		pl = 0
		b_lat_l = 90.0
		b_lon_l = 180.0
		b_lat_r = -90.0
		b_lon_r = -180.0

		ind = 0 

		stop_start = None
		prev_point = None

		maxp = MAXPOINTS
		for point in DBGeo.get_items_by_range(self.skey, dtfrom, dtto, maxp):
			d = max(MS, max(abs(plat - point['lat']), abs(plon - point['lon'])))
			plat = point['lat']
			plon = point['lon']

			if prev_point:
				dist = geo.distance(point, prev_point)
				dt = point['time'] - prev_point['time']
				dt = dt.days * 24 * 3600 + dt.seconds
				cspeed = (dist * 3600 / dt) if dt>0 else 0
				if cspeed > 300:			# Надеюсь таким образом избавиться от глюков
					continue
			else:
				dist = 0
				dt = 0
				cspeed = 0

			prev_point = point
				
			points.append([
				#local.toUTC(point['time']).strftime("%d/%m/%Y %H:%M:%S"),
				local.fromUTC(point['time']).strftime("%y%m%d%H%M%S"),
				plat, #point['lat'],
				plon, #point['lon'],
				int(point['course']),
				#20,
				int(round(log(DS/d, 2), 0)),
				#{'dist': dist, 'speed': point['speed'], 'dt': dt, 'speed2': cspeed},
			])
			l_lat.append((plat, ind))
			#l_lon.append((plon, ind))

			#if point['speed'] < 1.0:

			if point['fsource'] in (2, 3, 7):
				if stop_start is None:
					stop_start = {}
					stop_start['ind'] = max(0, ind-1)
					#stop_start['ind'] = ind
					stop_start['lat'] = plat
					stop_start['lon'] = plon
			if point['fsource'] == 6:
				if stop_start is not None:
					stops.append({
						'i': stop_start['ind'],
						'p': (stop_start['lat'], stop_start['lon']),
						's': ind,
					})
					stop_start = None
			"""
			if point['fsource'] in (2, 3, 7):
				if stop_start is None:
					stop_start = {}
					stop_start['ind'] = ind
					stop_start['lat'] = plat
					stop_start['lon'] = plon
					stops.append({'i': ind, 'p': (plat, plon)})
				else:
					if stop_start['lat'] != plat or stop_start['lon'] != plon:
						stop_start['ind'] = ind
						stop_start['lat'] = plat
						stop_start['lon'] = plon
						stops.append({'i': ind, 'p': (plat, plon)})
			"""


			b_lat_l = min(b_lat_l, plat)
			b_lon_l = min(b_lon_l, plon)
			b_lat_r = max(b_lat_r, plat)
			b_lon_r = max(b_lon_r, plon)

			ind += 1

		# Zoom для первой и последней точки наивысший (отображать всегда)
		plen = len(points) 
		if plen>0:
			points[0][4] = 0
			points[-1][4] = 0

		# Вычислим subbounds (TBD)

	
		# Разобьем на 8 частей по lat
		l_lat.sort()
		#l_lon.sort()
		subbounds = []

		if 'nosubbounds' not in options:
			sbs_lat = int(sqrt(plen) / 24) + 1
			sbs_lon = int(sqrt(plen) / 24) + 1
			for i in range(sbs_lat):
				l_lon = []
				i1 = plen * i // sbs_lat
				i2 = plen * (i+1) // sbs_lat
				#logging.info('i1 = %s' % str(i1))
				#logging.info('i2 = %s' % str(i2))
				for i3 in xrange(i1, i2):
					l_lon.append((points[l_lat[i3][1]][2], l_lat[i3][1]))
				l_lon.sort()
				for j in range(sbs_lon):
					sbl = []
					j1 = len(l_lon) * j // sbs_lon
					j2 = len(l_lon) * (j+1) // sbs_lon
					#logging.info(' j1 = %s' % str(j1))
					#logging.info(' j2 = %s' % str(j2))
					nmin_lat = 180
					nmax_lat = -180
					for j3 in xrange(j1, j2):
						nmin_lat = min(nmin_lat, points[l_lon[j3][1]][1])
						nmax_lat = max(nmax_lat, points[l_lon[j3][1]][1])
						sbl.append(l_lon[j3][1])
					if(len(sbl)):
						subbounds.append({
							#'sw': (l_lat[i1][0], l_lon[j1][0]),
							#'ne': (l_lat[i2-1][0], l_lon[j2-1][0]),
							'sw': (nmin_lat, l_lon[j1][0]),
							'ne': (nmax_lat, l_lon[j2-1][0]),
							'i': sbl,
						})
		#subbounds.append(((b_lat_l, b_lon_l), ((b_lat_l+b_lat_r)/2, (b_lon_l+b_lon_r)/2)))

		return {
			'answer': 'ok',
			#'bcount': len(recs),
			'count': len(points),
			#'counts': counts,
			'format': ["date", "lat", "lon", "course", "minzoom"],
			'points': points,
			'stops': stops,
			'bounds': {'sw': (b_lat_l, b_lon_l), 'ne': (b_lat_r, b_lon_r)},
			'subbounds': subbounds,
			#'slat': l_lat,
			#'slon': l_lon,
		}
		#self.response.out.write(json.dumps(jsonresp, separators=(',',':')) + "\r")

		"""
		prof = "gc AFTER:\n"
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		logging.info(prof)

		gc.collect()

		prof = "gc COLLECT:\n"
		prof += "gc.get_count()=%s\n" % repr(gc.get_count())
		prof += "gc.get_debug()=%s\n" % repr(gc.get_debug())
		prof += "gc.get_threshold()=%s\n" % repr(gc.get_threshold())
		prof += "gc.isenabled()=%s\n" % repr(gc.isenabled())
		#prof += "gc.get_objects()=%s\n" % repr(gc.get_objects())
		logging.info(prof)
		"""

class Geo_Info(webapp.RequestHandler):
	def get(self):
		from time import sleep
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
		skey = self.request.get("skey")
		if skey is None:
			self.response.out.write(json.dumps({'answer': None}) + "\r")
			return

		system_key = db.Key(skey)
		dtpoint = local.toUTC(datetime.strptime(self.request.get("point"), "%y%m%d%H%M%S"))
		#pointr = DBGeo.get_by_date(system_key, dtpoint)
		#point = None
		#if pointr:
		#	point = pointr.get_item_by_dt(dtpoint)

		point = DBGeo.get_by_datetime(system_key, dtpoint)
		
		jsonresp = {
			'answer': 'ok',
			'point': {
				#'count': pointr.i_count,
				'lat': point['lat'],
				'lon': point['lon'],
				'speed': '%.1f' % point['speed'],
				'course': point['course'],
				'vout': '%.1f' % point['vout'],
				'vin': '%.2f' % point['vin'],
				'sats': point['sats'],
				'fsource': point['fsourcestr'],
			},
			#'bcount': len(recs),
			#'count': len(points),
			#'counts': counts,
			#'format': ["date", "lat", "lon", "course", "minzoom"],
			#'points': points, 
			#'bounds': {'sw': (b_lat_l, b_lon_l), 'ne': (b_lat_r, b_lon_r)},
			#'subbounds': subbounds,
			#'slat': l_lat,
			#'slon': l_lon,
		}
		if SERVER_NAME=='localhost':
			sleep(0.3)
		self.response.out.write(json.dumps(jsonresp) + "\r")

class Geo_Dates(webapp.RequestHandler):
	def get(self):
		from bisect import insort
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
		skey = self.request.get("skey")
		if skey is None:
			self.response.out.write(json.dumps({'answer': None}) + "\r")
			return

		month = self.request.get("month")
		if month is None:
			self.response.out.write(json.dumps({'answer': None}) + "\r")
			return

		sy = int(month[:4])
		sm = int(month[4:])

		ny = sy
		nm = sm + 1
		if nm > 12:
			nm = 1
			ny += 1

		system_key = db.Key(skey)

		#req = DBGeo.all(keys_only=True).ancestor(system_key).filter('date >=', datetime(sy,sm,1)).filter('date <', datetime(ny,nm,1)).order('date').fetch(31*3) # пачки по 8 часов
		req = DBGeo.all().ancestor(system_key).filter('date >=', datetime(sy,sm,1)).filter('date <', datetime(ny,nm,1)).order('date').fetch(31*3) # пачки по 8 часов

		#dates = []
		#months = []
		days = []
		dlen = 0
		for rec in req:
			dlen+=1;
			"""
			#dt = rec.name()[4:12]
			dt = rec.key().name()[4:12]
			y = int(dt[0:4])
			m = int(dt[4:6])
			d = dt[6:8]
			"""

			dt = local.fromUTC(rec.get_first()['time']).strftime("%Y%m%d")
			#logging.info(dt)
			y = int(dt[0:4])
			m = int(dt[4:6])
			d = int(dt[6:8])

			if y == sy and m == sm:
				if d not in days:
					insort(days, d)

			dt = local.fromUTC(rec.get_last()['time']).strftime("%Y%m%d")
			#logging.info(dt)
			y = int(dt[0:4])
			m = int(dt[4:6])
			d = int(dt[6:8])

			if y == sy and m == sm:
				if d not in days:
					insort(days, d)

			#if dt not in dates:
			#	dates.append("%s" % dt)

		jsonresp = {
			'answer': 'ok',
			#'dates': dates,
			#'months': months,
			'year': sy,
			'month': sm,
			'days': days,
			'len': dlen,
		}

		self.response.out.write(json.dumps(jsonresp, indent=2) + "\r")	#sort_keys=True,



class Geo_Last(BaseApi):
	requred = ('account')
	def parcer(self, **argw):
		skey = self.request.get("skey", None)
		if skey is not None:
			systems = [db.get(db.Key(skey))]
		else:
			systems = self.account.systems
		recs = []
		for s in systems:
			recs.append({
				'skey': str(s.key()),
				'imei': s.imei,
				'desc': s.desc,
				'data': geo.getGeoLast(s.key()),
			})

		return {
			'answer': 'ok',
			'imeis': repr([r.imei for r in systems]),
			'geo': recs,
			#'dates': dates,
			#'months': months,
			#'years': years,
			#'len': dlen,
		}

class Geo_Count(BaseApi):
	requred = ('skey')
	def parcer(self):
		count = DBGeo.get_items_count(self.skey)
		return {'answer': 'ok',
			'count': count,
		}

class Geo_Report(BaseApi):
	requred = ('skey')
	def parcer(self):
		points = []

		#after = self.request.get('after', 'today')
		dtfrom = local.toUTC(datetime.strptime(self.request.get("from"), "%y%m%d%H%M%S"))
		dtto = local.toUTC(datetime.strptime(self.request.get("to"), "%y%m%d%H%M%S"))

		for point in DBGeo.get_items_by_range(self.skey, dtfrom, dtto, MAXPOINTS):
			points.append((
				local.fromUTC(point['time']).strftime("%H:%M:%S"),
				point['lat'], point['lon'],
				point['sats'],
				point['vout'],
				point['vin'],
				point['speed'],
				0, 0, 0
			));

		return {'answer': 'ok',
			'format': ('datetime', 'lat', 'lon', 'sats', 'vout', 'vin', 'speed'),
			#'points': points[::-1]		# Выдадим в обратной последовательности
			'points': points
		}

class Report_Get(BaseApi):
	requred = ('skey')
	def parcer(self):
		from math import log, sqrt

		#pfrom = self.request.get("from")
		dtfrom = local.toUTC(datetime.strptime(self.request.get("from"), "%y%m%d%H%M%S"))

		dtto = local.toUTC(datetime.strptime(self.request.get("to"), "%y%m%d%H%M%S"))

		report = []
		stop_start = None
		move_start = None
		prev_point = None
		state = 0	# 0 - stop   1 - move
		length = 0
		sum_length = 0	# Пройденая дистанция
		sum_tmove = 0	# Общее время в пути
		events = {}

		for point in DBGeo.get_items_by_range(self.skey, dtfrom, dtto, MAXPOINTS):
			if move_start is None:
				move_start = point

			if point['fsource'] in (2, 3, 7):
				if stop_start is None:
					if prev_point:
						stop_start = prev_point
					else:
						stop_start = point

					dura = (stop_start['time'] - move_start['time'])
					dura = dura.days * 24 * 3600 + dura.seconds
					sum_tmove += dura
					report.append({
						'type': 'move',
						'start': {
							'time': local.fromUTC(move_start['time']).strftime("%y%m%d%H%M%S"),
							'pos': (move_start['lat'], move_start['lon']),
						},
						'stop': {
							'time': local.fromUTC(stop_start['time']).strftime("%y%m%d%H%M%S"),
							'pos': (stop_start['lat'], stop_start['lon']),
						},
						'duration': dura,
						#'durationtxt': str(dura),
						'length': "%.3f" % length,
						'startpos': (point['lat'], point['lon']),
						'speed': (length * 3600 / dura) if dura!=0 else 0,
						'fsource': point['fsource'],
						'events': events,
					})
					events = {}

			elif point['fsource'] == 6:
				if stop_start is not None:
					dura = (point['time'] - stop_start['time'])
					dura = dura.days * 24 * 3600 + dura.seconds
					report.append({
						'type': 'stop',
						'start': {
							'time': local.fromUTC(stop_start['time']).strftime("%y%m%d%H%M%S"),
							'pos': (stop_start['lat'], stop_start['lon']),
						},
						'stop': {
							'time': local.fromUTC(point['time']).strftime("%y%m%d%H%M%S"),
							'pos': (point['lat'], point['lon']),
						},
						'duration': dura,
						#'durationtxt': str(dura),
						'length': 0,
						'startpos': (point['lat'], point['lon']),
						'speed': 0,
						'fsource': point['fsource'],
						'events': events,
					})
					events = {}
					state = 1	# Начало движения
					length = 0	# Пока не проехали нисколько
					move_start = point
					stop_start = None

			if prev_point:
				d = geo.distance(point, prev_point)
				td = point['time'] - prev_point['time']
				td = td.days * 24 * 3600 + td.seconds
				if td > 0:
					sp = d * 3600 / td
					if sp > 300:	# Максимальная скорость 300 км/ч
						#d = 0
						if 'path_break' not in events:
							events['path_break'] = local.fromUTC(point['time']).strftime("%y%m%d%H%M%S")
						continue
			else:
				d = 0
			length += d
			sum_length += d
			prev_point = point


		return {
			'answer': 'ok',
			'dtfrom': str(local.fromUTC(dtfrom)),
			'dtto': str(local.fromUTC(dtto)),
			'summary': {
				'length': sum_length, #"%.3f" % sum_length,
				'movetime': sum_tmove,
				'speed': (sum_length * 3600 / sum_tmove) if (sum_tmove!=0) else 0
			},
			'report': report,
		}

class Sys_Add(BaseApi):
	requred = ('account', 'imei')
	def parcer(self, **argw):
		res = self.account.AddSystem(self.imei)
		if res == 0:
			return {'answer': 'no', 'result': 'not found'}
		elif res == 2:
			return {'answer': 'no', 'result': 'already'}

		updater.inform_account('change_slist', self.account, {'type': 'Adding'})

		return {'answer': 'yes', 'result': 'added'}

class Sys_Del(BaseApi):
	requred = ('account', 'imei')
	def parcer(self, **argw):
		res = self.account.DelSystem(self.imei)
		if res == 0:
			return {'answer': 'no', 'result': 'not found'}
		elif res == 2:
			return {'answer': 'no', 'result': 'already'}
		updater.inform_account('change_slist', self.account, {'type': 'Deleting'})
		return {'answer': 'yes', 'result': 'deleted'}

class Sys_Sort(BaseApi):
	requred = ('account', 'imei')
	def parcer(self, **argw):
		index = self.request.get('index', None)
		if index is None:
			return {'result': 'no', 'reason': 'index not defined'}
		index = int(index)

		systems = self.account.systems
		slist = [s.imei for s in systems]
		if self.imei not in slist:
			return {'result': 'no', 'reason': 'unknown system imei'}

		oldindex = slist.index(self.imei)

		logging.info(
			'\n=====\n OLD index ' + str(oldindex) +
			'\nIMEI_1: ' + db.get(self.account.systems_key[oldindex]).imei +
			#'\nIMEI_2: ' + systems[oldindex].imei +
			'\nIMEI_S: ' + self.imei
		)
		logging.info( '\n ==\n' + repr(systems))
		logging.info( '\n ==\n' + repr(slist))
		logging.info( '\n ==\n' + repr(self.account.systems_key))

		if oldindex != index:
			#logging.info('\nchange ' + str(account.systems_key[oldindex]) + ' and ' + str(account.systems_key[index]))
			#logging.info('change ' + db.get(account.systems_key[oldindex]).imei + ' and ' + db.get(account.systems_key[index]).imei)

			goted = self.account.systems_key[oldindex]
			del self.account.systems_key[oldindex]
			self.account.systems_key.insert(index, goted)
			logging.info('\n=====Change ' + str(goted) + '(' + db.get(goted).imei + ') to ' + str(index))

			#account.systems_key[oldindex],account.systems_key[index] = account.systems_key[index],account.systems_key[oldindex]
			self.account.put()

		#res = account.AddSystem(imei)
		#if res == 0:
		#	return {'result': 'not found'}
		#elif res == 2:
		#	return {'result': 'already'}
		updater.inform_account('change_slist', self.account, {'type': 'Sorting'})

		return {'result': 'sorted', 'desc': {'imei': self.imei, 'oldindex': oldindex, 'newindex': index}}

class Sys_Desc(BaseApi):
	requred = ('account', 'imei')
	def parcer(self, **argw):
		desc = self.request.get('desc', None)
		if desc is None:
			return {'answer': 'no', 'reason': 'desc not defined'}

		system = self.account.system_by_imei(self.imei)
		if system is None:
			return {'answer': 'no', 'reason': 'nosys'}
		system.desc = desc
		system.put()

		updater.inform('changedesc', system.key(), {
			'desc': desc
		})

		return {'result': 'ok', 'imei': system.imei, 'desc': system.desc}

class Sys_Config(BaseApi):
	requred = ('imei')
	def parcer(self, **argw):
		#from zlib import decompress
		from datamodel import DBConfig, DBDescription, DBNewConfig

		cmd = self.request.get('cmd', None)
		if cmd is None:
			return {'answer': 'no', 'reason': 'cmd not defined'}

		# Запросить список программируемых параметров
		if cmd == 'get':
			descriptions = DBDescription().all() #.fetch(MAX_TRACK_FETCH)

			descs={}
			fdescs={}
			for description in descriptions:
				descs[description.name] = description.value
				fdescs[description.name] = {
					'name': description.name,
					'value': description.value,
					'unit': description.unit,
					'coef': description.coef,
					'mini': description.mini,
					'maxi': description.maxi,
					'private': description.private
				}

			config = DBConfig.get_by_imei(self.imei)
			configs = config.config
			'''
			if config.config:
				configs = eval(decompress(config.config))
			else:
				configs = {}
			'''
			waitconfigs = DBNewConfig.get_by_imei(self.imei)
			waitconfig = waitconfigs.config
			'''
			if waitconfigs.config:
				waitconfig = eval(decompress(waitconfigs.config))
			else:
				waitconfig = {}
			'''
			nconfigs = {}

			for config, value in configs.items():
				#desc = u"Нет описания"
				desc = None	#u"Нет описания"
				fdesc = None
				if config in descs:
					desc = descs[config]
					fdesc = fdescs[config]
				else:
					pass
					#continue

				if config in waitconfig: wc = waitconfig[config]
				else: wc = None

				nconfigs[config] = {
					'type': configs[config][0],
					'value': configs[config][1],
					'default': configs[config][2],
					'desc': desc,
					'fdesc': fdesc,
					'wait': wc
				}

				"""
				if config in waitconfig:
					nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], waitconfig[config], desc, fdesc)
				else:
					nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], None, desc, fdesc)
					#configs[config] = (configs[config][0], configs[config][1], configs[config][2], configs[config][1])
				"""

			# Для удобства отсортируем словарь в список
			#sconfigs = sortDict(configs)
			sconfigs = [(key, nconfigs[key]) for key in sorted(nconfigs.keys())]

			return {
				'answer': 'ok',
				'config': sconfigs,
				'raw': configs
			}

		# Установить параметр
		if cmd == 'set':
			#from zlib import compress, decompress
			name = self.request.get('name', 'unknown')
			value = self.request.get('value', '0')

			waitconfigs = DBNewConfig.get_by_imei(self.imei)
			waitconfig = waitconfigs.config
			'''
			if waitconfigs.config:
				waitconfig = eval(decompress(waitconfigs.config))
			else:
				waitconfig = {}
			'''
			waitconfig[name] = value
			waitconfigs.config = waitconfig #compress(repr(waitconfig), 9)
			waitconfigs.put()

		# Отменить задание (действие аналогичное /params?cmd=check&imei=xxxxxxxx)
		if cmd == 'cancel':
			newconfigs = DBNewConfig().get_by_imei(self.imei)
			newconfigs.config = {}
			newconfigs.put()

		return {'result': 'ok'}

class Param_Desc(BaseApi):
	def parcer(self):
		from datamodel import DBDescription

		name = self.request.get('name', '-error-')
		DBDescription(key_name = "dbdescription_%s" % name, name=name, value=self.request.get('value', '')).put()
		return {'result': 'ok'}

"""
class Global_DelAll(BaseApi):
	def parcer(self, **argw):
		geos = DBGeo.all(keys_only=True).fetch(1000)
		db.delete(geos)
		return {'answer': 'ok'}
"""

class Logs_Get(BaseApi):
	requred = ('skey')
	def parcer(self):
		from datamodel import GPSLogs

		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		cursor = self.request.get("cursor", None)
		
		logsq = GPSLogs.all().ancestor(self.skey).order('-date').fetch(1000)

		"""
		logs = []
		for log in logsq:
			logs.append({
				'time': log.ldate.strftime("%d/%m/%Y %H:%M:%S"),
				'text': log.text,
				'label': log.label,
				'key': "%s" % log.key()
			})
                """
                # Более короткая и понятная запись. Интересно будет сравнить производительность на очень большом списке
		logs = [{
				'time': log.ldate.strftime("%d/%m/%Y %H:%M:%S"),
				'text': log.text,
				'label': log.label,
				'key': "%s" % log.key()
			} for log in logsq]

		return {
			"answer": "ok",
			"logs": logs,
		}
		
class Chanel_GetToken(BaseApi):
	requred = ('account')
	def parcer(self):
		import updater

		uuid = self.request.get("uuid")
		if uuid is None:
			return {'answer': 'no', 'reason': 'uuid not defined or None'};

		token = updater.register(self.account, uuid)

		return {
			'answer': 'ok',
			'akey': '%s' % self.account.key(),
			'uuid': uuid,
			'token': token
		}

class SystemConfig(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		akey = self.request.get('akey', None)
		if akey is None:
			return {'answer': 'no', 'reason': 'akey not defined or None'};

		account = DBAccounts.get(db.Key(akey))

		self.response.out.write(json.dumps(account.getconfig) + "\r")

	def post(self):
		from urllib import unquote_plus
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		akey = self.request.get('akey', None)
		if akey is None:
			return {'answer': 'no', 'reason': 'akey not defined or None'};

		#logging.info(self.request.body)
		#logging.info(unquote_plus(self.request.body))
		#logging.info(repr(self.request.body))
		#logging.info(self.request.arguments())

		account = DBAccounts.get(db.Key(akey))

		config = account.getconfig()
		#newconfig = {(k:self.request.get(k)) for k in self.request.arguments()}
		newconfig = dict((k, self.request.get(k)) for k in self.request.arguments())
		#newconfig = {}
		#for k in self.request.arguments():
		#	newconfig[k] = self.request.get(k)

		config.update(newconfig)

		#logging.info(repr(newconfig))
		#config.
		#for k in self.request.arguments():
		#	if k in config
		account.putconfig(config)

		self.response.out.write(json.dumps(config) + "\r")

application = webapp.WSGIApplication(
	[
	('/api/info.*', Info),
	('/api/version.*', Version),
	('/api/debug_jqGrid.*', Debug_jqGrid),
	('/api/debug_geo.*', DebugGeo),
	('/api/get_geo.*', GetGeo),

	('/api/geo/del.*', Geo_Del),
	('/api/geo/get*', Geo_Get),
	('/api/geo/dates*', Geo_Dates),
	('/api/geo/info*', Geo_Info),
	('/api/geo/last*', Geo_Last),
	('/api/geo/count*', Geo_Count),
	('/api/geo/report*', Geo_Report),

	('/api/report/get*', Report_Get),

	('/api/sys/add*', Sys_Add),
	('/api/sys/del*', Sys_Del),
	('/api/sys/desc*', Sys_Desc),
	('/api/sys/sort*', Sys_Sort),
	('/api/sys/config*', Sys_Config),

	('/api/param/desc*', Param_Desc),

	('/api/logs/get*', Logs_Get),

	('/api/chanel/gettoken*', Chanel_GetToken),

	#('/api/global/delall*', Global_DelAll),

	('/api/system/config*', SystemConfig),

	#('/api/geo/test*', Geo_Test),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
