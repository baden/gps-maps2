print "Hello, world!!!"

print 1

foo = [1,2,3,4]
for i in foo:
	print i

class aa:
	def __init__(self, name):
		self.name = name
		print "__init__[%s]" % self.name

	def __del__(self):
		print "__flush__[%s]" % self.name

	def __repr__(self):
		return "Ahha-ha [%s]" % self.name

	def foo(self):
		print "__foo__[%s]" % self.name

	@classmethod
	def auto(cls):
		print "auto"
		return [cls("auto1"), cls("auto2")]

a = aa("name1")
print a
a.foo()
del(a)
b = aa.auto()
print repr(b)

