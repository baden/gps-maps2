# -*- coding: utf-8 -*-
from google.appengine.api import channel
from google.appengine.api import memcache
from django.utils import simplejson as json
import logging


"""
	Связи между клиентом и списком систем для обновления
"""

#class DBUpdater(db.Model):
#	system = db.ReferenceProperty(DBUser, collection_name='logs')


"""
	Когда клиент открывает страницу, он устанавливает соединение по токену, полученному данной функцией
	Необходимо сохранить связи между системой и подключенными клиентами
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
	В силу сложности реализации для каждого клиента только последнее открытое окно будет автоматически обновляться
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
