# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.api import memcache
from django.utils import simplejson as json
import logging


"""
	Связи между клиентом и списком систем для обновления
"""

class DBUpdater(db.Model):
	#account = db.ReferenceProperty(DBUser, collection_name='updater')
	#uuids = db.StringListProperty(default=None)	# Список последних 10 подключений (стек)
	uuids = db.ListProperty(str, default=None)	# Список последних 10 подключений (стек)
	#tokens = db.StringListProperty(default=None)	# Список последних 10 токенов (стек)

	"""
		Создает тунель, связывает uuid с аккаунтом
		Возвращает токен соединения
	"""
	@classmethod
	def register(cls, account, uuid):
		def txn():
			token = channel.create_channel(uuid)
			logging.info("UPDATER: Register token[%s] for account[%s] uuid[%s]" % (token, account.user.email(), uuid))
			logging.info("UPDATER: account=%s" % account.key())
			#update = False
			entity = cls.get_by_key_name("updater_%s" % account.key())
			if entity is None:
				#entity = cls("updater_%s" % account.key(), uuids=[uuid], tokens=[token])
				entity = cls(key_name="updater_%s" % account.key(), uuids=[uuid])
				#entity.uuids=[uuid]
				entity.put()
				memcache.set("updater_%s" % account.key(), [uuid])
				return token

			# Если уже есть записи, то добавим uuid для данного аккаунта по принципу стека 10 последних значений

			# TBD! Стоит проверить возможность повторного использования токенов для одного и того-же uuid!
			#if uuid in entity.uuid:
			#	return token
			entity.uuids.append(uuid)
			if len(entity.uuids) > 10:
				del entity.uuids[0]
			entity.put()

			memcache.set("updater_%s" % account.key(), entity.uuids)

			return token

		return db.run_in_transaction(txn)

	@classmethod
	def inform(cls, msg, system, comment):
		from datamodel import DBAccounts

		logging.info("UPDATER: Inform msg[%s] for system[%s] comment[%s]" % (msg, system.imei, comment))
		
		# Если маленькое сомнение что фильтер будет работать так как я предполагаю.
		# Возможно будет проверка только по первому элементу, я не очень понял документацию

		# Этот запрос тоже наверное можно оптимизировать через memcache (вобщето даже желательно)
		allacc = DBAccounts.all().filter('systems_key =', system.key()).fetch(1000)
		for account in allacc:
			logging.info("UPDATER: account=%s" % account.user.email())
			logging.info("UPDATER: account=%s" % account.key())
			uuids = memcache.get("updater_%s" % account.key())
			if uuids is None:
				entity = cls.get_by_key_name("updater_%s" % account.key())
				if entity is None:
					logging.info("UPDATER: NOT FOUND")
					continue
				uuids = entity.uuids

			logging.info("UPDATER: uuids=" % uuids)

			for uuid in uuids:
				logging.info("Update for account[%s] uuid[%s]" % (account.user.email(), uuid))
				message = {
					'msg': '%s' % msg,
					'account': {
						'akey': '%s' % account.key(),
						'email': account.user.email(),
					},
					'skey': '%s' % system.key(),
					'imei': system.imei,
					'comment': comment,
					'systems': len(allacc)
				}
				channel.send_message(uuid, json.dumps(message))


"""
	Когда клиент открывает страницу, он устанавливает соединение по токену, полученному данной функцией
	Необходимо сохранить связи между системой и подключенными клиентами
"""
register = DBUpdater.register
inform = DBUpdater.inform
"""
def register(account, uuid):
	token = channel.create_channel(uuid)

# Попробуем связать два последних канала (стек)
#	memcache.set("token_%s_0" % account, uuid)
	memcache.set("token_%s" % account.key(), uuid)

	logging.info("SET Memcache: token_%s=%s" % (account, uuid))
	#memcache.set("token_last", token)
	#memcache.set("token_last_cid", uuid)

	#for sys in account.systems:
	#	logging.info("connect system[%s] to uuid[%s]" % (sys, uuid) )

	return token
"""


"""
	В силу сложности реализации для каждого клиента только последнее открытое окно будет автоматически обновляться
"""
"""
def inform(msg, system, comment):
	from datamodel import DBAccounts

	# Если маленькое сомнение что фильтер будет работать так как я предполагаю.
	# Возможно будет проверка только по первому элементу, я не очень понял документацию

	# Этот запрос тоже наверное можно оптимизировать через memcache (вобщето даже желательно)
	allacc = DBAccounts.all().filter('systems_key =', system.key()).fetch(1000)
	for account in allacc:
		uuid = memcache.get("token_%s" % account.key())
		if uuid:
			logging.info("Update for account[%s] uuid[%s]" % (account.user.email(), uuid))
			message = {
				'msg': '%s' % msg,
				'skey': '%s' % system.key(),
				'imei': system.imei,
				'comment': comment,
				'systems': len(allacc)
			}
			channel.send_message(uuid, json.dumps(message))
"""
