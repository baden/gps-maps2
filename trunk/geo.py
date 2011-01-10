# -*- coding: utf-8 -*-

from local import fromUTC
from google.appengine.api import memcache
from datamodel import DBGeo


def repr_short(point):
	return [
		fromUTC(point['time']).strftime("%y%m%d%H%M%S"),
		point['lat'], #point['lat'],
		point['lon'], #point['lon'],
		int(point['course']),
	]

def repr_middle(point):
	return {
		#'count': pointr.i_count,
		'time': fromUTC(point['time']).strftime("%Y-%m-%d %H:%M:%S"),	# dt
		'lat': point['lat'],
		'lon': point['lon'],
		'speed': '%.1f' % point['speed'],
		'course': point['course'],
		'vout': '%.1f' % point['vout'],
		'vin': '%.2f' % point['vin'],
		'sats': point['sats'],
		#'fsource': point['fsourcestr'],
	}

def getGeoLast(system):
	value = memcache.get("geolast_%s" % str(system.key()))
	if value is not None:
		return value

	req = DBGeo.all().ancestor(system).order('-date').fetch(1)
	if req:
		rec = req[0]
		point = rec.get_last()
		tail = []
		if rec.count > 10:
			for i in xrange(rec.count-2, rec.count-10, -1):
				tail.append(repr_short(rec.get_item(i)))

		value = {
			'point': repr_middle(point),
			'tail': tail,
			'tailformat': ["date", "lat", "lon", "course"],
		}
		memcache.add("geolast_%s" % str(system.key()), value)
		#logging.info("\n\n=== geolast_%s\n\n" % str(system.key()))

		return value
	else:
		return None

"""
	При получении новых гео-данных необходимо вызвать эту процедуру для сброса memcache
"""
def updateLasts(system):
	memcache.delete("geolast_%s" % str(system.key()))

def distance(p1, p2):
	from math import pi, sin, cos, atan2, sqrt
	R = 6371; # km (change this constant to get miles)
	dLat = (p2['lat']-p1['lat']) * pi / 180.0
	dLon = (p2['lon']-p1['lon']) * pi / 180.0
	a = sin(dLat/2.0) * sin(dLat/2.0) + cos(p1['lat'] * pi / 180.0) * cos(p2['lat'] * pi / 180.0) * sin(dLon/2.0) * sin(dLon/2.0)
	d = R * 2.0 * atan2(sqrt(a), sqrt(1-a))
	#if (d>1) return Math.round(d)+"km";
	#else if (d<=1) return Math.round(d*1000)+"m";
	return d	# Результат в км