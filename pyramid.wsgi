import sys

sys.path.insert(0, '/var/www/html/prelims_scheduler/venv_prelims/lib/python3.8/site-packages')

from pyramid.paster import get_app, setup_logging
ini_path = '/var/www/html/prelims_scheduler/production.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
