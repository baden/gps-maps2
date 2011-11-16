# -*- coding: utf-8 -*-

__author__ = "Batrak Denis"

import os
import logging

#from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#os.environ['CONTENT_TYPE'] = "application/octet-stream"

class DBExport(db.Model):
	etype = db.StringProperty(multiline=False)	# тип экспортируемого документа
	data = db.BlobProperty()			# Экспортированный документ

class XLS(webapp.RequestHandler):
	def post(self):
		#self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

		#import io
		from StringIO import StringIO
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
		ws0 = wb.add_sheet(u'Отчет')

		borders = [Borders() for i in range(7)]

		# Стили заголовка
		borders[0].left = 1
		borders[0].top = 1
		borders[0].bottom = 1

		borders[1].top = 1
		borders[1].bottom = 1

		borders[2].right = 1
		borders[2].top = 1
		borders[2].bottom = 1

		# Стили тела таблицы
		borders[3].left = 1
		#borders[4].left = 1
		#borders[5].left = 1
		borders[6].right = 1

		style = [XFStyle() for i in range(7)]
		for i in range(7): style[i].borders = borders[i]

		ws0.write(0, 0, u'Действие', style[0])
		ws0.write(0, 1, u'Примечание', style[1])
		ws0.write(0, 2, u'Период', style[1])
		ws0.write(0, 3, u'Время', style[2])

    		#datestyle.num_format_str = fmt

		i = 1
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
			j = 0
			for cell in line:
				ws0.write(i, j, cell, style[j+3])
				j += 1
			i += 1

		ws0.col(0).width = 3000
		ws0.col(1).width = 14000
		ws0.col(2).width = 4500
		ws0.col(3).width = 2600

		#ws0.write_merge(5, 8, 6, 10, "")

        	#import CompoundDoc
        	#doc = CompoundDoc.XlsDoc()

		#self.response.out.write(wb.get_biff_data())

		#wb.save('blanks.xls')
		#wb.save(self.response.out)

		#out = io.BytesIO()
		out = StringIO()
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
			rec = DBExport.get(db.Key(key))
			self.response.out.write(rec.data)
			db.delete(rec)
	

application = webapp.WSGIApplication(
	[
		('/export/xls.*', XLS),
		('/export/get.*', Get),
	],
	debug=True
)

def main():
	#os.environ['CONTENT_TYPE'] = "application/octet-stream"
	logging.getLogger().setLevel(logging.DEBUG)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
