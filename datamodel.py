# -*- coding: utf-8 -*-

from google.appengine.ext import db
#from local import fromUTC

from datetime import datetime, timedelta
import struct
#import zlib
import logging
import pickle

"""
 Запись о пользователе
"""

DEFAULT_CONFIG = repr({
	'timezone': +2,
	'theme': 'cupertino',
})

#class DBAccounts(db.Expando):
class DBAccounts(db.Model):
	user = db.UserProperty()						# Пользователь
	name = db.StringProperty(multiline=False, default=u"Имя не задано")	# Отображаемое имя
	#systems = db.StringListProperty()					# Перечень наблюдаемых систем (их keys)
	systems_key = db.ListProperty(db.Key, default=None)			# Перечень наблюдаемых систем (их keys)
	#systems = db.ListProperty(db.Blob)					# Перечень наблюдаемых систем
	register = db.DateTimeProperty(auto_now_add=True)			# Дата регистрации аккаунта
	config_list = db.StringProperty(multiline=True, default=DEFAULT_CONFIG)	# Список записей конфигурации
	access = db.IntegerProperty(default=0)					# Уровень доступа
										# 0-только просмотр, 1-возможность конфигурирования, 2-возможность правки данных и т.д.
	@property
	def systems(self):
		#return 'aaa'
		system_list = []
		purge = False
		#for i in range(len(self.systems_key)):
		for i, rec in enumerate(self.systems_key):
			s = db.get(rec)
			if s is not None:
				system_list.append(s)
			else:
				del self.systems_key[i]
				purge = False
		if purge:
			self.put()
		return system_list

	# Возвращает True если система с таким key контроллируется аккаунтом
	def has_skey(self, skey):
		return skey in systems_key

	def system_by_imei(self, imei):
		if imei not in [s.imei for s in self.systems]:
			return None
		return DBSystem.get_or_create(imei)
	
	def RegisterSystem(self, imei):
		system = DBSystem.get_by_key_name("sys_%s" % imei)
		if system is None:
			system = DBSystem(key_name = "sys_%s" % imei, imei=imei)
			system.put()

		if system.key() not in self.systems_key:
			self.systems_key.append(system.key())
			self.put()

	def AddSystem(self, imei):
		system = DBSystem.get_by_key_name("sys_%s" % imei)
		if system is None:
			return 0

		if system.key() not in self.systems_key:
			self.systems_key.append(system.key())
			self.put()
			return 1
		return 2

	def DelSystem(self, imei):
		system = DBSystem.get_by_key_name("sys_%s" % imei)
		if system is None:
			return 0

		if system.key() in self.systems_key:
			self.systems_key.remove(system.key())
			self.put()
			return 1
		return 2

	@property
	def single(self):
		return len(systems_key) == 1

	@property
	def config(self):
		from repy import simplejson as json
		return json.dumps(self.getconfig(), indent=2)

	@property
	def pconfig(self):
		return self.getconfig()

	def getconfig(self):
		#configs = pickle.loads(self.config_list)
		#for rec in self.config_list:
		#	configs.append(eval(rec))
		return eval(self.config_list)

	def putconfig(self, configdict):
		self.config_list = repr(configdict)
		self.put()

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
										# Без премиум-подписки функционал ограничен.
										# история ограничена 14 днями, и т.д.
	#@property
	#def ldate(self):
	#	return self.date

	@classmethod
	def get_by_imei(cls, imei):
		return cls.get_by_key_name("sys_%s" % imei)
	
	@classmethod
	def get_or_create(cls, imei, phone=None, desc=None):
		def txn():
			update = False
			entity = cls.get_by_key_name("sys_%s" % imei)
			if entity is None:
				entity = cls(key_name="sys_%s" % imei, imei=imei)
				update = True
			if phone is not None:
				if entity.phone != phone:
					entity.phone = phone
					update = True
			if desc is not None:
				if entity.desc != desc:
					entity.desc = desc
					update = True
			if update:
				entity.put()
			return entity

		return db.run_in_transaction(txn)

	''' Тоже что и функция get_or_create, только возвращает значение ключа.
		используется когда нужен только ключ, и сами данные не обязательны. Записи phone и desc не обновляются.
		дополнительно кешируется.
	'''
	@classmethod
	def getkey_or_create(cls, imei, phone=None, desc=None):
		from google.appengine.api import memcache
		value = memcache.get("skey_by_imei_%s" % imei)
		if value is not None:
			return db.Key(value)
		else:
			key = cls.get_or_create(imei).key()	# Это не самое элегантное решение, но я другого не вижу пока.
			value = memcache.set("skey_by_imei_%s" % imei, "%s" % key)
			return key


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
 Каждатя пачка данных содержит точки за 8 часов времени.
 Запись имеет ключ вида: geo_YYYYMMDDHH
 где
	YYYY - год
	MM - месяц
	DD - день
	HH - часы [00,08,16]
 Максимальное количество точек в одной записи = 60*60*8 = 28800 точек (*36 = 1036800 байт ~ 0.99МБ)

 !Предложение!
 По результатам реальных тестов, оказывается что очень много пакетов содержит всего 48 точки (6 точек в час).
 Предлагается переделать процедуру сохранения точек по принципу:
 создается один пакет для точек за сутки:
  ключ вида: geo_YYYYMMDD
 В него добавляются точки как обычно.
 Если при очередном добавлении количество точек достигает 28800 штук, то создаются пакеты
  geo_YYYYMMDDHH (столько сколько нужно с шагом 8 часов) и работа с ними идет как обычно.

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

#PACK_STR = 'iffffffBBBBiiiiiiii'
PACK_STR = 'iffffffBBBBi'
#           ^^^^^^^^^^^^
#           │││││││││││└ res3 (int)
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
PACK_LEN = 36
MAX_RECS = 1024*1024//PACK_LEN		# Максимальное количество точей в одной записи

assert(struct.calcsize(PACK_STR) == PACK_LEN)
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
		try:
			fsourcestr = FSOURCE[u[8]]
		except KeyError:
			fsourcestr = 'unknown'

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
			'fsourcestr': fsourcestr,
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
			0, 0, 0#,  0, 0, 0, 0, 0, 0, 0	# Reserve
		)

	def get_item(self, offset):
		return self.u_to_v(struct.unpack_from(PACK_STR, self.bin, offset * PACK_LEN))

	def get_first(self):
		return self.get_item(0)

	def get_last(self):
		#return self.get_item(self.count-1)
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

	def find_item_index(self, t):
		lo = 0
		hi = self.count
		while lo < hi:
			mid = (lo+hi)//2
			if self.time(mid) < t: lo = mid+1
			else: hi = mid
		return lo

	def test_4_sort(self):
		logging.info('-------- Test 4 sort TBD --------------')
		return True
	
	def add_point(self, point):
		#logging.info('--------  add_point --------------')
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


		lo = self.find_item_index(t)

		#if lo < self.count:
		if self.time(lo) == t:		# Элемент уже есть в базе (игнорируем)
			return False

		self.bin = self.bin[:lo*PACK_LEN] + self.v_to_p(point) + self.bin[lo*PACK_LEN:]

		#self.test_4_sort()
		
		self.i_count += 1
		return True

	def get_item_by_dt(self, pdt):
		t = (pdt.hour & 7)*60*60 + pdt.minute * 60 + pdt.second
		return self.get_item(self.find_item_index(t))

	@classmethod
	def key_by_date(cls, pdate):
		return pdate.strftime("geo_%Y%m%d") + "%02d" % (pdate.hour & ~7)

	@classmethod
	def get_by_date(cls, skey, pdate):
		return cls.get_by_key_name(cls.key_by_date(pdate), parent=skey)

	@classmethod
	def get_by_datetime(cls, skey, dtpoint):
		#return cls.get_by_key_name(cls.key_by_date(pdate), parent=skey)
		#dtpoint = local.toUTC(datetime.strptime(self.request.get("point"), "%d%m%Y%H%M%S"))
		pointr = cls.get_by_date(skey, dtpoint)
		if pointr:
			point = pointr.get_item_by_dt(dtpoint)
			return point
		else:
			return None

	@classmethod
	def get_items_by_range(cls, system_key, dtfrom, dtto, maxp):
		dhfrom = datetime(dtfrom.year, dtfrom.month, dtfrom.day, dtfrom.hour & ~7, 0, 0)
		dhto = datetime(dtto.year, dtto.month, dtto.day, dtto.hour & ~7, 0, 0)
		recs = DBGeo.all().ancestor(system_key).filter("date >=", dhfrom).filter("date <=", dhto).order("date")#.fetch(1000)
		for rec in recs:
			logging.info('==> API:GEO:GET  fetch DBGeo[%s]' % rec.key().name())
			if maxp == 0: break
			for point in rec.get_all():
				if point['time'] < dtfrom:	# Это очень не оптимально, нужно заменить поиском (TBD)
					continue
				if point['time'] > dtto:
					break

				if maxp == 0: break
				else: maxp -= 1

				yield point
	@classmethod
	def get_tail_items(cls, system_key, count=1):
		recs = DBGeo.all().ancestor(system_key).order("-date")
		prev = None
		antiloop = 1000
		for rec in recs:
			for i in range(rec.count-1, -1, -1):
				antiloop -= 1
				if antiloop<=0: return

				item = rec.get_item(i)
				if prev == (item['lat'], item['lon']): continue
				prev = (item['lat'], item['lon'])
				#logging.info('Get_Tail_Items: Lat = %f  Lon = %f' % prev)
				yield item
				count -= 1
				if count<=0: return

	# Подсчитывает общее количество точек в базе
	@classmethod
	def get_items_count(cls, system_key, maxp = 1000):
		recs = DBGeo.all().ancestor(system_key).order("-date")
		count = 0
		rcount = 0
		for rec in recs:
			count += rec.count
			rcount += 1
		return {'points': count, 'records': rcount}

class PointWorker(object):
	def __init__(self, skey):
		logging.info('PointWorker: __init__(%s)' % str(skey))
		self.last_pkey = None
		self.rec = None
		self.rec_changed = False
		self.system_key = skey
		self.nrecs = 0

	def Add_point(self, point):
		if point is None: return
		#h = point['time'].hour & ~7;
		#pkey = point['time'].strftime("geo_%Y%m%d") + "%02d" % (point['time'].hour & ~7)
		pkey = DBGeo.key_by_date(point['time'])
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
					date = datetime(point['time'].year, point['time'].month, point['time'].day, point['time'].hour & ~7, 0, 0)
				)
				self.nrecs = 0
			else:
				self.nrecs = self.rec.count

		#point['seconds'] = point['time'].minute * 60 + point['time'].second
		point['seconds'] = (point['time'].hour & 7)*60*60 + point['time'].minute * 60 + point['time'].second

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


"""
	События не привязанные точно ко времени (включения/выключения, получение/выполнение SMS-команд и т.д.)
"""
class GPSLogs(db.Model):
	text = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	mtype = db.StringProperty(default=None)	# Тип сообщения: none-обычное сообщение, debug-отладочное сообщение, alarm-срочное сообщение и т.д.
	label = db.IntegerProperty(default=0)		# Числовая метка для определения групп сообщений. (пока не используется)
	pos = db.GeoPtProperty()

	#@property
	#def ldate(self):
	#	#return fromUTC(self.date).strftime("%d/%m/%Y %H:%M:%S")
	#	return fromUTC(self.date)

"""
	Конфигурация системы
"""

from zlib import compress, decompress
'''
class DBConfig(db.Model):
	#cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения конфигурации
	config = db.BlobProperty()
	#strconfig = db.TextProperty()

	@classmethod
	def get_by_imei(cls, imei):
		return cls.get_or_insert("dbconfig_%s" % imei)
		"""
		def txn():
			entity = cls.get_by_key_name("dbconfig_%s" % imei)
			if entity is None:
				entity = cls(key_name="dbconfig_%s" % imei)
				#entity.put()	# И сразу сохраним
				
			return entity

		return db.run_in_transaction(txn)
		"""
'''

class DBConfig(db.Model):
	#cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения конфигурации
	_config = db.BlobProperty()
	#strconfig = db.TextProperty()

	@classmethod
	def get_by_imei(cls, imei):
		return cls.get_or_insert("%s" % imei)

	def get_config(self):
		if self._config:
			try:
				configs = eval(decompress(self._config))
			except:
				configs = {}
		else:
			configs = {}
		return configs

	def set_config(self, value):
		self._config = compress(repr(value), 9)
		#self.put()

	def del_config(self):
		#del self._config
		self._config = None

	config = property(get_config, set_config, del_config, "I'm the 'config' property.")

class DBNewConfig(DBConfig):
	pass

class DBDescription(db.Model):
	name = db.StringProperty(multiline=False)	# имя параметра
	value = db.StringProperty(multiline=False)	# Текстовое описание
	unit = db.StringProperty(multiline=False)	# Единица измерения
	coef = db.FloatProperty(default=1.0)		# Коэффициент преобразования для человеческого представления
	mini = db.IntegerProperty(default=0)		# Минимальное значение для типа INT
	maxi = db.IntegerProperty(default=32767)	# Максимальное значение для типа INT
	private = db.BooleanProperty(default=False)


class DBFirmware(db.Model):
	cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения прошивки
	boot = db.BooleanProperty(default=False)	# Устанавливается в True если это образ загрузчика
	hwid = db.IntegerProperty()			# Версия аппаратуры
	swid = db.IntegerProperty()			# Версия прошивки
	subid = db.IntegerProperty(default=0)		# Подверсия аппаратуры (введена из-за 6000ков)
	data = db.BlobProperty()			# Образ прошивки
	size = db.IntegerProperty()			# Размер прошивки (опция)
	desc = db.StringProperty(multiline=True)	# Описание прошивки (опция)

# Гео-зоны
# parent (ancestor) является администратором зоны (DBAccounts)
class DBZone(db.Model):
	ztype = db.StringProperty(required=True, choices=set(["poligon", "circle", "bound"]))	# на первом этапе будет поддерживаться только 'poligon'
	points = db.ListProperty(db.GeoPt, default=None)			# Перечень узлов
	options = db.StringListProperty(default=None)				# свойства зоны (цвет, и т.п.)
	name = db.StringProperty(default=u'Задайте имя зоны');
	address = db.StringProperty(default=u'Укажите адрес для зоны');
	boundssw = db.GeoPtProperty()						# Оптимизация поиска вхождения точки
	boundsne = db.GeoPtProperty()

# Записи связи зон с объектами
# parent (ancestor) указывает на объект (DBSystem)
class DBZoneLink(db.Model):
	#system = db.
	sort = db.IntegerProperty(default=0)		# приоритет правила (для поднятия приоритета указать -1, для уменьшения приоритета указать +1)
	zone = db.ReferenceProperty(DBZone)
	rule = db.IntegerProperty(default=0)		# правило 

