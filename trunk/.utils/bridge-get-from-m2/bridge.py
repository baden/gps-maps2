#!/usr/bin/python
# -*- coding: utf-8 -*-
# bridge.py

import sys
import httplib
import urllib
import socket

# Где взять данные
#GETFROM = "127.0.0.1:80"
GETFROM = "gps-maps2.appspot.com:80"

# Куда отправить
#HOST = "127.0.0.1"
#PORT = 80
#HOST = "gps-maps.appspot.com"
#PORT = 80
#HOST = "212.110.139.65"
#PORT = 8015

# Какая система
#SYS = 2

#IMAGE = "binbackup-16.09.2010"
#IMEI = ("0", "356895035376246", "356895035358996", "353358016204856", "356895035359317")
#IMEI = ("0", "35689503537624601", "35689503535899601", "35335801620485601")	#Fake

IMEI = sys.argv[1]

#SYSTEMS = (2)

#import codecs
#outf = codecs.getwriter('cp866')(sys.stdout)
##outf = codecs.getwriter('cp1251')(sys.stdout)

def main():
	try:
		aftercdate = open("bridge.lastcdate.%s" % IMEI, "r").read()
	except:
		aftercdate = "None"

	print(u"Метка времени: %s" % aftercdate)

	print(u"Запрос более свежих данных...")

	conn = httplib.HTTPConnection(GETFROM)
	#conn.set_debuglevel(1)
	#conn.request("GET", "/binbackup?cmd=pack&imei=%s&after=%s" % (IMEI[SYS], urllib.quote(aftercdate)))
	#conn.request("GET", "/binbackup?cmd=pack&cnt=1000&imei=%s&after=%s" % (IMEI[SYS], urllib.quote(aftercdate)))
	conn.request("GET", "/binbackup?cmd=pack&cnt=1000&imei=%s&after=%s&asc=yes" % (IMEI, urllib.quote(aftercdate)))
	response = conn.getresponse()
	#print response.status, response.reason
	data = response.read()
	conn.close()
	#print data

	bindata = response.getheader("BinData", None)

	if not bindata or bindata=="None":
		print(u"Нет точек. Обновление не требуется.")
		return

	if len(data) == 0:
		print(u"Получен пустой пакет. Обновление не требуется.")
		return

	lastcdate = response.getheader("lastcdate", None)
	print(u"Размер данных: %d" % len(data))
	print(u"Метка времени полученных данных: %s" % lastcdate)

	file("raw.%s.%s.bin" % (IMEI, lastcdate), "wb").write(data)
	

	if lastcdate:
		print(u"Сохранение метки времени")
		#try:
		file("bridge.lastcdate.%s" % IMEI, "w").write("%s" % lastcdate)


if __name__ == "__main__":
	print('--------------------------------------------------------------------')
	print(u"     Синхронизация системы IMEI:%s" % IMEI)
	print('--------------------------------------------------------------------')
	#print >> outf, u"Синхронизация для системы %s" % IMEI
	main()
