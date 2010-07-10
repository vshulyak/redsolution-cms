# -*- coding: utf-8 -*-
from xmlrpc_urllib2_transport import ProxyTransport
from django.conf import settings
from pkg_resources import Distribution
import xmlrpclib
import os

def search_index(query):
    # Using PYPI XMLRPC improved serach
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi', transport=ProxyTransport())
    return client.search({'name': query})

def update_pythonpath(abspath):
    if 'PYTHONPATH' in os.environ:
        os.environ['PYTHONPATH'] += '%s%s' % (os.pathsep, abspath)
    else:
        os.environ['PYTHONPATH'] = '%s' % abspath

def get_bulidout(abspath):
    # include parts dir into environment PYTHONPATH so setuptools can 
    # search modules there
    update_pythonpath(abspath)
    try:
        from setuptools.command import easy_install
    except ImportError:
        try:
            from ez_setup import main
            main(['--install-dir=%s' % abspath, ])
        except SystemExit:
            pass
        else:
            from setuptools.command import easy_install

    easy_install.main(['--install-dir=%s' % abspath, 'zc.buildout'])

    egg_name = filter(lambda x: 'zc.buildout' in x, os.listdir(abspath))[0]
    bulidout_dist = Distribution.from_location(os.path.join(abspath, egg_name), 'zc.buildout')
    bulidout_dist.activate()

def install(modules):
    '''
    Install module in givan path
    Module sould be dictionary object, returned by xmlrpc server pypi:
    Example:
        {'_pypi_ordering': 16,
         'name': 'django-tools',
         'summary': 'miscellaneous tools for django',
         'version': '0.10.0.git-ce3ec2d',
    }
    Returns WorkingSet object, 
    see
        http://peak.telecommunity.com/DevCenter/PkgResources#workingset-objects
    terminology:
         http://mail.python.org/pipermail/distutils-sig/2005-June/004652.html
    '''
    # make path absolute
    abspath = settings.PARTS_DIR
    get_bulidout()
    import zc.buildout

    return zc.buildout.easy_install.install(['%s==%s' % (module_['name'], module_['version'])
        for module_ in modules], abspath)

def test():
    print 'Searching module mptt'
    modules = search_index('mptt')
    if modules:
        print 'found %s modules' % len(modules)
    workset = install([modules[0]])
    mptt_distr = workset.by_key['django-mptt']
    print 'Trying to import mptt'
    mptt_distr.activate()
    from mptt.exceptions import InvalidMove
    print 'Successfull!'

if __name__ == '__main__':
    # run with no parameters for basic test case.
    test()
