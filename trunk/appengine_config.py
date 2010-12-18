def webapp_add_wsgi_middleware(app):
   from google.appengine.ext.appstats import recording
   return recording.appstats_wsgi_middleware(app)

"""
apptrace_URL_PATTERNS  = ['^/$']
apptrace_TRACE_MODULES = ['gps-api.py', 'gps-bingps.py']

def webapp_add_wsgi_middleware(app):
    from apptrace.middleware import apptrace_middleware
    return apptrace_middleware(app)
"""
