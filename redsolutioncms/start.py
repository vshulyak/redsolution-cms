# -*- coding: utf-8 -*-
import os
import shutil
import sys
import subprocess
from os.path import join, dirname 

home_dir = join(os.getenv('HOME'), '.redsolutioncms')

def install_in_home(flush=True):
    '''Copy nessesary files to home folder''' 
    
    if flush:
        # check target dir doesn't exists
        if os.path.exists(home_dir):
            try:
                shutil.rmtree(home_dir)
            except:
                print 'Can not write into home dir: %s. Check permissions' % home_dir
                raise
        shutil.copytree(join(dirname(__file__), 'home'), home_dir)
    else:
        raise NotImplementedError('Not defined yet')

def run_bootstrap():
    cmd = '%(python)s %(bootstrap)s' % {
        'python': sys.executable,
        'bootstrap': join(home_dir, 'bootstrap.py')
    }
    # run python boostrap.py from home installation dir 
    cwd = os.getcwd()
    os.chdir(home_dir)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

def run_buildout():
    cmd = '%(python)s %(buildout)s' % {
        'python': sys.executable,
        'buildout': join(home_dir, 'bin/buildout')
    }
    cwd = os.getcwd()
    os.chdir(home_dir)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

def run_syncdb():
    cmd = '%(python)s %(django)s syncdb --noinput' % {
        'python': sys.executable,
        'django': join(home_dir, 'bin/django')
    }
    cwd = os.getcwd()
    os.chdir(home_dir)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

def run_wrapper():
    cmd = '%(python)s %(django)s wrap_runserver' % {
        'python': sys.executable,
        'django': join(home_dir, 'bin/django')
    }
    cwd = os.getcwd()
    os.chdir(home_dir)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

if __name__ == '__main__':
    print '1. Copying files to home dir'
    install_in_home()
    print '2. Bootstraping'
    run_bootstrap()
    print '3. Building'
    run_buildout()
    print '4. Syncdb'
    run_syncdb()
    print '5. Run wrapper'
    run_wrapper()