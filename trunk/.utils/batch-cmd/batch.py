#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py
import httplib

SERVER = "gps-maps.appspot.com:80"

def main():
	#imei = "861785000709935"
	#cmd = 
	conn = httplib.HTTPConnection(SERVER)
	conn.request("GET", "/api/sys/secure_list")
	response = conn.getresponse()
	#print response.status, response.reason
	data = response.read()
	conn.close()
	#print cmd
	#print data
	imeis = []
	for line in data.split('\n'):
		start = line.find('imei')
		if start > 0:
			fimei = line[start+8:start+8+15]
			if len(fimei) == 15:
				imeis.append(fimei)

	for imei in imeis:
		print imei
		#continue
		conn = httplib.HTTPConnection(SERVER)
		#conn.request("GET", "/api/sys/config?cmd=set&imei=%s&name=gps.send.move&value=5" % imei)
		conn.request("GET", "/api/sys/add?akey=aghncHMtbWFwc3IpCxIKREJBY2NvdW50cyIZYWNjXzExMDgxMDYwODk2NDQ4ODU1MzI2OAw&imei=%s" % imei)

		response = conn.getresponse()
		#print response.status, response.reason
		data = response.read()
		conn.close()

if __name__ == "__main__":
	main()
