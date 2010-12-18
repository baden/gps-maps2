# -*- coding: utf-8 -*-

from google.appengine.ext import db
from local import fromUTC

from datetime import datetime, timedelta
import struct
#import zlib
import logging

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
	
	@classmethod
	def get_or_create(cls, imei, phone=None, desc=None):
		def txn():
			update = False
			entity = cls.get_by_key_name("sys_%s" % imei)
			if entity is None:
				entity = cls(key_name="sys_%s" % imei, imei=imei)
				update = True
			if phone:
				if entry.phone != phone:
					entry.phone = phone
					update = True
			if desc:
				if entry.desc != desc:
					entry.desc = desc
					update = True
			if update:
				entity.put()
			return entity

		return db.run_in_transaction(txn)


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
 Каждатя пачка данных содержит точки за 4 часа времени.
 Запись имеет ключ вида: geo_YYYYMMDDHH
 где
	YYYY - год
	MM - месяц
	DD - день
	HH - часы [00,04,08,12,16,20]
 Максимальное количество точек в одной записи = 60*60*4 = 14400 точек (*64 = 921600 байт)
 Необходимо позаботиться о том, чтобы размер одной записи не превысил 72 байт. (ограничение пачки в 1 МБ)

 !Предложение!
 По результатам реальных тестов, оказывается что очень много пакетов содержит всего 24 точки (6 точек в час).
 Предлагается переделать процедуру сохранения точек по принципу:
 создается один пакет для точек за сутки:
  ключ вида: geo_YYYYMMDD
 В него добавляются точки как обычно.
 Если при очередном добавлении количество точек достигает 14400 штук, то создаются пакеты
  geo_YYYYMMDDHH (столько сколько нужно с шагом 4 часа) и работа с ними идет как обычно.

 Т.е. другими словами при поиске точек в Workere, сначала ищется пакет с ключем geo_YYYYMMDD, и если таковой не
 найден, то пакет с ключем geo_YYYYMMDDHH.

 Процедуру Geo_Get, похоже, переделывать не придется.

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
#           ││││└─────── course (float)
#           │││└──────── speed (float)
#           ││└───────── lon (float)
#           │└────────── lat (float)
#           └─────────── seconds (int)
PACK_LEN = 64
# !!! time должен всегда! идти первым и иметь тип int(i)

class DBGeo(db.Model):
	date = db.DateTimeProperty()				# Дата/время смещения
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
			'seconds': u[0], 
			'time': self.date + timedelta(seconds = u[0]),
			'lat': u[1],
			'lon': u[2],
			'speed': u[3],
			'course': u[4],
			'vout': u[5],
			'vin': u[6],
			'sats': u[7],
			'fsource': u[8],
		}
	def v_to_p(self, t):
		return struct.pack(PACK_STR,
			t['seconds'],
			t['lat'],
			t['lon'],
			t['speed'],
			t['course'],
			t['vout'],
			t['vin'],
			t['sats'],
			t['fsource'],
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0	# Reserve
		)


	def get_item(self, offset):
		return self.u_to_v(struct.unpack_from(PACK_STR, self.bin, offset * PACK_LEN))

	def get_last(self):
		return self.u_to_v(struct.unpack_from(PACK_STR, self.bin, (self.count-1) * PACK_LEN))

	def get_all(self, reverse=False):
		if reverse:
			start = len(self.bin) - PACK_LEN	# Я несколько не уверен на счет правильности
			stop = -1
			step = -PACK_LEN
		else:
			start = 0
			stop = len(self.bin)
			step = PACK_LEN

		for offset in xrange(start, stop, step):
			yield self.u_to_v(struct.unpack_from(PACK_STR, self.bin, offset))

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

		t = point['seconds']

		# Как правило данные поступают последовательно и нет смысла искать место вставки, просто нужно добавить данные в конец
		if t > self.time(self.count-1):
			self.bin += self.v_to_p(point)
			self.i_count += 1
			return True

		#if t in self.timelist():	# Это не очень оптимальная процедура (возможно стоит ее совместить с поиском)
		#	return False

		# Поиск места вставки
		
		# Версия №2. Вроде работает.

		lo = 0
		hi = self.count
		while lo < hi:
			mid = (lo+hi)//2
			if self.time(mid) < t: lo = mid+1
			else: hi = mid

		if self.time(lo) == t:		# Элемент уже есть в базе (игнорируем)
			return False

		self.bin = self.bin[:lo*PACK_LEN] + self.v_to_p(point) + self.bin[lo*PACK_LEN:]
		

		"""
		# Поиск места вставки
		s = 0
		e = self.count-1

		while (s+1) < e:
			m = (s+e) // 2
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
		"""

		self.i_count += 1
		return True

class PointWorker(object):
	def __init__(self, skey):
		logging.info('PointWorker: __init__(%s)' % str(skey))
		self.last_pkey = None
		self.rec = None
		self.rec_changed = False
		self.system_key = skey
		self.nrecs = 0

	def Add_point(self, point):
		#h = point['time'].hour & ~3;
		pkey = point['time'].strftime("geo_%Y%m%d") + "%02d" % (point['time'].hour & ~3)
		#logging.info('PointWorker: Add_point(%s)' % pkey)
		if pkey != self.last_pkey:
			if self.last_pkey is not None:
				self.Flush()
			self.last_pkey = pkey
			self.rec = DBGeo.get_by_key_name(pkey, parent=self.system_key)
			if self.rec is None:
				self.rec = DBGeo(
					parent = self.system_key,
					key_name = pkey,
					date = datetime(point['time'].year, point['time'].month, point['time'].day, point['time'].hour & ~3, 0, 0)
				)
				self.nrecs = 0
			else:
				self.nrecs = self.rec.count

		#point['seconds'] = point['time'].minute * 60 + point['time'].second
		point['seconds'] = (point['time'].hour & 3)*60*60 + point['time'].minute * 60 + point['time'].second

		change = self.rec.add_point(point)
		if change:
			self.nrecs += 1
			self.rec_changed = True

	def Flush(self):
		logging.info('PointWorker: Flush (%d recs)' % self.nrecs)
		if (self.rec is not None) and self.rec_changed:
			self.rec.put()
		self.rec = None
		self.rec_changed = False
		self.nrecs = 0

	def __del__(self):
		self.Flush()


class DBGPSBin(db.Model):
	dataid = db.IntegerProperty()
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)

class DBGPSBinBackup(db.Model):
	cdate = db.DateTimeProperty(auto_now_add=True)
	dataid = db.IntegerProperty()
	crcok = db.BooleanProperty(default=False)
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)
