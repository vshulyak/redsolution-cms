# -*- coding: utf-8 -*-
from xmlrpc_urllib2_transport import ProxyTransport
from zc.buildout import easy_install
import xmlrpclib
import os


def search_index(query):
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi', transport=ProxyTransport())
    return client.search({'name': query})


def install(modules, path='parts'):
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
    if not path.startswith('/'):
        abspath = os.path.join(os.path.dirname(__file__), path)
    else:
        abspath = path
    if not os.path.exists(path):
        os.makedirs(path)

    return easy_install.install(['%s==%s' % (module_['name'], module_['version'])
        for module_ in modules], path)

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
