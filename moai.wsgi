import sys
import os
import site
import tempfile


os.environ['PYTHON_EGG_CACHE'] = tempfile.mkdtemp(prefix='moai-egg-cache-')

site.addsitedir(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'lib',
                             'python%d.%d' % sys.version_info[:2],
                             'site-packages'))

from paste.deploy import loadapp
application = loadapp(
    'config:%s' % os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                               'settings.ini'))
