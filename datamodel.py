# -*- coding: utf-8 -*-

from google.appengine.ext import db
from local import fromUTC

"""
 Запись о пользователе
"""

class DBAccounts(db.Expando):
	user = db.UserProperty()						# Пользователь
	name = db.StringProperty(multiline=False, default=u"Имя не задано")	# Отображаемое имя
	#systems = db.StringListProperty()					# Перечень наблюдаемых систем (их keys)
	systems_key = db.ListProperty(db.Key, default=None)			# Перечень наблюдаемых систем (их keys)
	#systems = db.ListProperty(db.Blob)					# Перечень наблюдаемых систем
	register = db.DateTimeProperty(auto_now_add=True)			# Дата регистрации аккаунта
	config_list = db.ListProperty(unicode, default=[u"{timezone:0}"])	# Список записей конфигурации
	access = db.IntegerProperty(default=0)					# Уровень доступа
										# 0-только просмотр, 1-возможность конфигурирования, 2-возможность правки данных и т.д.										 
	@property
	def systems(self):
		#return 'aaa'
		system_list = []
		for rec in self.systems_key:
			system_list.append(db.get(rec))
		return system_list

	def RegisterSystem(self, imei):
		system = DBSystem.get_by_key_name("sys_%s" % imei)
		if system is None:
			system = DBSystem(key_name = "sys_%s" % imei, imei=imei)
			system.put()

		if system.key() not in self.systems_key:
			self.systems_key.append(system.key())
			self.put()

	@property
	def single(self):
		return len(systems_key) == 1

	@property
	def config(self):
		configs = []
		for rec in self.config_list:
			configs.append(eval(rec))
		return configs

"""
 Запись о системе
"""

class DBSystem(db.Model):
	#userid = db.IntegerProperty()						# Unique
	imei = db.StringProperty(multiline=False)				# IMEI
	phone = db.StringProperty(multiline=False, default="None")		# Phone number, for example: +380679332332
	date = db.DateTimeProperty(auto_now_add=True)				# Дата регистрации системы
	desc = db.StringProperty(multiline=False, default=u"Нет описания")			# Описание
	premium = db.DateTimeProperty(auto_now_add=True)			# Дата окончания премиум-подписки (абон-плата).
										# Без премиум-подписки функционал ограничен.										# история ограничена 14 днями, и т.д.
	@property
	def ldate(self):
		#return fromUTC(self.date).strftime("%d/%m/%Y %H:%M:%S")
		return fromUTC(self.date)

"""
 Информация о последней известной координате
"""

class DBLastPos(db.Model):
	skey = db.StringProperty(multiline=False)		# Система
	lpos = db.GeoPtProperty()				# Позиция
	ldatetime = db.DateTimeProperty()			# Дата точки


"""
 Гео-данные
"""

class DBGeo(db.Model):
	gdate = db.DateProperty()
	