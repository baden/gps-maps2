#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

import socket

from glob import glob

HOST = "127.0.0.1"
PORT = 80

#HOST = "gps-maps2.appspot.com"
#PORT = 80

#HOST = "212.110.139.65"
#PORT = 8015

SYS = 1
IMAGE = "*.bin"
IMEI = ("123123", "356895035376246", "356895035358996", "353358016204856", "356895035359317", "353358019726996")
#IMEI = ("0", "35689503537624601", "35689503535899601", "35335801620485601")	#Fake

def senddatav2(f):
	if SYS>5:
		print("Support SYS=[1,3]. fail")
		return

	body = open(f, "rb").read()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Connect to %s:%d" % (HOST, PORT))
	s.connect((HOST, PORT))

	send = "POST /bingps?imei=%s&dataid=%d HTTP/1.1\r\n" % (IMEI[SYS], 0)
	send+= "Host: gps-maps2.appspot.com\r\n"
	send+= "Content-type: application/octet-stream\r\n"
	send+= "Content-Length: %d\r\n" % len(body)
	send+= "\r\n"
	#send+= body

	print(send)
	print("{BODY}\n")

	s.send(send)
	s.send(body)
	print("Wait answer...\n");
	while 1:
		s.settimeout(20.0);
		try:
			received = s.recv(1024)
		except:
			print('-timeout-')
			break
		if received:
			print received
			if received.find("BINGPS: OK")>0:
				print("-ok-")
				break
		else:
			print("-none-")
			break
			#if received.startswith("B"): break
	s.close()
	print("OK\n")

def main():
	print('--------------------------------------------------------------------')

#	senddata(0)
#	senddata(1)
	for f in glob(IMAGE):
		senddatav2(f)
		#break
	

if __name__ == "__main__":
	main()
