#from google.appengine.api import taskqueue
#from google.appengine.api.labs.taskqueue import Task
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import logging

class Counter(db.Model):
    count = db.IntegerProperty(indexed=False)

class CounterHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
	<html>
	<body>
	<form action="/testtask" method="post">
		<input type="submit">
	</form>
	ALL:
	""")
        self.response.out.write(repr(Counter.all()))
        self.response.out.write("""
	</body>
	</html>

	""")

    def post(self):
        key = self.request.get('key')

        # Add the task to the default queue.
        taskqueue.add(url='/testtask/worker', params={'key': key, 'data': '123'})
        #taskqueue.add(url='/testtask/worker?key=%s' % key, payload = '123')
	#Task(url='/testtask/worker?key=%s' % key, params = None, payload = '123')

        self.redirect('/testtask')

class CounterWorker(webapp.RequestHandler):
    def post(self): # should run at most 1/s
	logging.info("arguments: %s" % self.request.arguments())
	logging.info("body: %s" % len(self.request.body))
	return

        key = self.request.get('key')
        def txn():
            counter = Counter.get_by_key_name(key)
            if counter is None:
                counter = Counter(key_name=key, count=1)
            else:
                counter.count += 1
            counter.put()
        db.run_in_transaction(txn)

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/testtask/worker', CounterWorker),
        ('/testtask', CounterHandler),
    ]))

if __name__ == '__main__':
    main()
