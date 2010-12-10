# -*- coding: utf-8 -*-

from google.appengine.ext import db
from local import fromUTC

from datetime import datetime, timedelta
import struct

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

 Данные хранятся пачками.
 Каждатя пачка данных содержит точки за один час времени.
 Запись имеет ключ вида: geo_YYYYMMDDHH
 где
	YYYY - год
	MM - месяц
	DD - день
	HH - часы
 Максимальное количество точек в одной записи = 60*60 = 3600 точек
 Необходимо позаботиться о том, чтобы размер одной записи не превысил 291 байт. (ограничение пачки в 1 МБ)

 Записи представлены списком.
"""

FSOURCE = {
	0: "-",
	1: "SUDDENSTOP",
	2: "STOPACC",
	3: "TIMESTOPACC",
	4: "SLOW",
	5: "TIMEMOVE",
	6: "START",
	7: "TIMESTOP",
	8: "ANGLE",
	9: "DELTALAT",
	10: "DELTALONG",
	11: "DELTA",
}
PACK_STR = 'iffffffBBBBiiiiiiii'
#           ^^^^^^^^^^^-------- Reserve
#           │││││││││││
#           ││││││││││└─ res2 (byte)
#           │││││││││└── res1 (byte)
#           ││││││││└─── fsource (byte)
#           │││││││└──── sats (byte)
#           ││││││└───── vin (float)
#           │││││└────── vout (float)
#           ││││└─────── cource (float)
#           │││└──────── speed (float)
#           ││└───────── lon (float)
#           │└────────── lat (float)
#           └─────────── time (int)
PACK_LEN = 64
# !!! time должен всегда! идти первым и иметь тип int(i)

class DBGeo(db.Model):
	date = db.DateTimeProperty()				# Дата записи + часы (необходима, например, для возможности удаления старых записей)
	bin = db.BlobProperty(default=None)			# Упакованные данные
	# Остальные параметры, возможно будут использоваться только на этапе отладки и в продакшине будут убраны.
	i_count = db.IntegerProperty(default=0)			# Кол-во точек в пакете
	i_first = db.DateTimeProperty()				# Время первой точки
	i_last = db.DateTimeProperty()				# Время последней точки

	extend = db.ListProperty(unicode, default=None)		# Дополнительная информация за текущий период


	@property
	def count(self):
		if self.bin is None:
			return 0
		else:
			return len(self.bin) / PACK_LEN

	def u_to_v(self, u):
		return {
			'time': self.date + timedelta(seconds = u[0]),
			'lat': u[1],
			'lon': u[2],
			'speed': u[3],
			'cource': u[4],
			'vout': u[5],
			'vin': u[6],
			'sats': u[7],
			'fsource': u[8],
		}
	def v_to_p(self, t):
		return struct.pack(PACK_STR,
			t['time'],
			t['lat'],
			t['lon'],
			t['speed'],
			t['cource'],
			t['vout'],
			t['vin'],
			t['sats'],
			t['fsource'],
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0	# Reserve
		)

	def get_all(self, reverse=False):
		if reverse:
			start = self.count - 1
			stop = -1
			step = -PACK_LEN
		else:
			start = 0
			stop = self.count
			step = PACK_LEN

		for offset in xrange(start, stop, step):
			yield self.u_to_v(struct.unpack_from(PACK_STR, self.bin, offset))

	def get_item(self, offset):
		return self.u_to_v(struct.unpack_from(PACK_STR, self.bin, offset * PACK_LEN))

	def get_last(self):
		return self.u_to_v(struct.unpack_from(PACK_STR, self.bin, (self.count-1) * PACK_LEN))

	def timelist(self):
		stop = len(self.bin)
		for offset in xrange(0, stop, PACK_LEN):
			yield struct.unpack_from('i', self.bin, offset)[0]

	def time(self, index):
		return struct.unpack_from('i', self.bin, index * PACK_LEN)[0]

	def add_point(self, point):
		if self.count == 0:
			self.bin = self.v_to_p(point)
			self.i_count = 1
			return True

		t = point['time']

		# Как правило данные поступают последовательно и нет смысла искать место вставки, просто нужно добавить данные в конец
		if t > self.time(self.count-1):
			self.bin += self.v_to_p(point)
			self.i_count += 1
			return True

		#if t in self.timelist():	# Это не очень оптимальная процедура (возможно стоит ее совместить с поиском)
		#	return False

		# Поиск места вставки
		s = 0
		e = self.count-1

		while (s+1) < e:
			m = (s+e) / 2
			if self.time(m) > t:
				e = m
			else:
				s = m

		if self.time(s) == t:		# Элемент уже есть в базе (игнорируем)
			return False

		if self.time(e) == t:		# Элемент уже есть в базе (игнорируем)
			return False

		if self.time(s) > t:
			p = s
		else:
			if self.time(e) < t:
				p = e + 1
			else:
				p = e

		# Вставляем данные
		self.bin = self.bin[:p*PACK_LEN] + self.v_to_p(point) + self.bin[p*PACK_LEN:]
		self.i_count += 1
		return True
