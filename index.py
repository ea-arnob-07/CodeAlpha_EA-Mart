import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

_application = None
startup_error = None

try:
    from django.core.wsgi import get_wsgi_application
    _application = get_wsgi_application()
except Exception:
    import traceback
    startup_error = traceback.format_exc()

def app(environ, start_response):
    if startup_error:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [startup_error.encode('utf-8')]
    return _application(environ, start_response)
