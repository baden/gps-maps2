#!/usr/bin/python
# -*- coding: utf-8 -*-
# dist.py


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

p1 = {'lat': 48.4, 'lon': 32.1}
p2 = {'lat': 48.5, 'lon': 32.2}

print distance(p1, p2)
