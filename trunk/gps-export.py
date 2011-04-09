# -*- coding: utf-8 -*-

__author__ = "Batrak Denis"

import logging

#from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class DBExport(db.Model):
	etype = db.StringProperty(multiline=False)	# тип экспортируемого документа
	data = db.BlobProperty()			# Экспортированный документ

class XLS(webapp.RequestHandler):
	def post(self):
		#self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		import io
		import sys
		from repy import simplejson as json
		sys.path.insert(0, 'xlwt.zip')  # Add .zip file to front of path

		from xlwt import *

		#args = self.request.arguments()
		data = json.loads(self.request.get('data', '[]'))

		font0 = Font()
		font0.name = 'Times New Roman'
		font0.struck_out = True
		font0.bold = True

		style0 = XFStyle()
		style0.font = font0

		wb = Workbook()
		ws0 = wb.add_sheet('0')

		ws0.write(1, 1, 'Test', style0)

		#args.sort()
		#for i in range(0, 0x53):
		i = 0
		for line in data:
			#borders = Borders()
			#borders.left = i
			#borders.right = i
			#borders.top = i
			#borders.bottom = i

			#style = XFStyle()
			#style.borders = borders

			#ws0.write(i, 2, '', style)
			#ws0.write(i, 3, hex(i), style0)
			#ws0.write(i, 4, par)
			#ws0.write(i, 5, self.request.get(par, ''))
			j = 4
			for cell in line:
				ws0.write(i, j, cell)
				j += 1
			i += 1

		#ws0.write_merge(5, 8, 6, 10, "")

        	#import CompoundDoc
        	#doc = CompoundDoc.XlsDoc()

		#self.response.out.write(wb.get_biff_data())

		#wb.save('blanks.xls')
		#wb.save(self.response.out)

		out = io.BytesIO()
		wb.save(out)

		rec = DBExport()
		rec.etype = 'xls'
		rec.data = out.getvalue()
		rec.put()

		self.response.out.write(json.dumps(
			{'key': str(rec.key())},
			indent=2
		) + "\r")

class Get(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
		key = self.request.get('key', None)
		if key:
			rec = DBExport.get(key)
			self.response.out.write(rec.data)
	

application = webapp.WSGIApplication(
	[
		('/export/xls.*', XLS),
		('/export/get.*', Get),
	],
	debug=True
)

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
