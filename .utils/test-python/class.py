#!/usr/bin/python
# -*- coding: utf-8 -*-
# test01.py

#from json import simplejson as json
import json

class BaseApi(object):
	header = 'no header'
	out = 'no out'
	requred = None

	def parcer(self):
		return {'answer': 'no', 'reason': 'base api'}

	def _parcer(self):
		print('Requred: %s' % repr(self.requred))
		if 'a' in self.requred:
			print('a name are detected')
			self.a = 1000
		return self.parcer()

	def get(self):
		#self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
		#self.response.out.write
		self.header = 'text/javascript; charset=utf-8'

		self.out = json.dumps(self._parcer(), indent=2) + "\n"
		

class BaseAccApi(BaseApi):
	requred = ('a', 'b')
	def parcer(self):
		defret = super(BaseAccApi, self).parcer()
		#BaseApi.get(self)
		#self.out += ' BaseAccApi_get'

		print('My a value %s', self.a)

		return {'answer': 'yes', 'reason': 'BaseAcc api'}
	pass

"""
class Test1(object):
	#print 'Create'
	#name = '1qw234234234'
	#name2 = '1qw234234234'

	#__name__ = "Test1"
	var = 1

	def __new__(cls):
		print 'New Test1 ', type(cls).__name__
		return super(Test1, cls).__new__(cls)

	def __init__(self):
		print 'Init(base) ', type(self).__name__

	def __del__(self):
		print 'Del(base)', type(self).__name__

	#def __delattr__(self):
	#	print 'DelAttr ', type(self).__name__
	def __getattr__(self, m):
		print "GetAttr ", m
		return m

	def __setattr__(self, name, value):
		print 'SetAttr %s=%s' % (name, value)
		object.__setattr__(self, name, value)

	def __delattr__(self, name):
		print 'DelAttr %s' % name
		return object.__delattr__(self, name)


class Test2(Test1):
	#print 'Create'

	def __init__(self):
		print 'Init (%s) (var=%d)'% (type(self).__name__, self.var)
		#Test1.__del__(self)
		#super(Test1, self).__init__()
		Test1.__init__(self)

       	def __del__(self):
		#print '----------------'
		print 'Del %s (var=%d)' % (type(self).__name__, self.var)
		#self.__super__.__del__(self)
		print 'self = ', self
		print 'Test2 = ', Test2
		if Test2:
			super(Test2, self).__del__()

		#Test2.__del__(self)
		#super(Test2, self).__del__(self)

	#def __delattr__(self):
	#	print 'DelAttr'

	#def __setattr__(self, name, value):
	#	print 'SetAttr %s=%s' % (name, value)
	#	self['name'] = value

class Test3(object):
	pass
"""

def main():

	a = BaseAccApi()
	a.get()

	print(a.header)
	print(a.out)

	"""
	#t = Test1()
	r = Test2()
	s = r

	r.abc = 123
	print "abc = ", r.abc

	print "abcd = ", r.abcd

	#print globals()

	del r.abc
	#del r.abcd

	#print "Test1", dir(Test1)
	#print "Test2", dir(Test2)
	#print "Test3", dir(Test3)
	#print dir(t)

	#del t

	# поиск = 1
	print u'Удаляем r'
	#del r
	print u'Удаляем s'
	#del s
	"""

main()

#print globals()
