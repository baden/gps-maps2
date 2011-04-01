# -*- coding: utf-8 -*-
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from datetime import date, timedelta, datetime

from datamodel import DBAccounts

SERVER_NAME = os.environ['SERVER_NAME']
VERSION = '0'
if 'CURRENT_VERSION_ID' in os.environ: VERSION = os.environ['CURRENT_VERSION_ID'] + '/1'

class TemplatedPage(webapp.RequestHandler):
	def __init__(self):
		self.user = users.get_current_user()
		if self.user == None:
			self.accounts = None
			return

		self.account = DBAccounts.get_by_key_name("acc_%s" % self.user.user_id())

		if self.account is None:
			self.account = DBAccounts(key_name = "acc_%s" % self.user.user_id())
			self.account.user = self.user
			self.account.put()

	def write_template(self, values, alturl=None):
		if self.user:
			#url = users.create_logout_url(self.request.uri)
			login_url = users.create_login_url(self.request.uri)
			values['login_url'] = login_url
			values['now'] = datetime.utcnow()
			values['username'] = self.user.nickname()
			values['admin'] = users.is_current_user_admin()
			values['server_name'] = SERVER_NAME
			values['uid'] = self.user.user_id()
			values['account'] = self.account

			values['environ'] = os.environ
			values['version'] = VERSION

			if alturl:
				path = os.path.join(os.path.dirname(__file__), 'templates', alturl)
			else:
				path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
			#self.response.headers['Content-Type']   = 'text/xml'
			self.response.out.write(template.render(path, values))
		else:
			#self.response.out.write("<html><body>")
			#self.response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
			#self.response.out.write("Нажмите <a href=" + users.create_login_url(self.request.uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
			#self.response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
			#self.response.out.write("</body></html>")
			self.redirect(users.create_login_url(self.request.uri))
