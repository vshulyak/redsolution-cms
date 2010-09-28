# -*- coding: utf-8 -*-
import os
import shutil
import sys
import subprocess
from os.path import join, dirname
from optparse import OptionParser

# Home dir defined here!
home_dir = join(os.getenv('HOME'), '.redsolutioncms')
project_dir = os.getcwd()

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

def run_cmd(cmd, cmd_dict=None):
    # I splitted this function in two for API usage in CMS task system
    cmd = process_cmd_string(cmd, cmd_dict)
    run_in_home(cmd)

def process_cmd_string(cmd, cmd_dict=None):
    if cmd_dict is None:
        cmd_dict = {
            'python': sys.executable,
            'bootstrap': join(home_dir, 'bootstrap.py'),
            'buildout': join(home_dir, 'bin/buildout'),
            'django': join(home_dir, 'bin/django'),
        }
    return cmd % cmd_dict

def run_in_home(cmd):
    # run python boostrap.py from home installation dir 
    cwd = os.getcwd()
    os.chdir(home_dir)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--continue', action='store_true', dest='continue_install',
        help="Continue installation, doesn't delete old files", default=False)
    
    (options, args) = parser.parse_args()
    # TODO: Find installed CMS automatically and ask user, does he want to delete old files
    
    if not options.continue_install:
        print '1. Copying files to home dir'
        install_in_home()
    print '2. Bootstraping'
    run_cmd('%(python)s %(bootstrap)s')
    print '3. Building'
    run_cmd('%(python)s %(buildout)s')
    print '4. Syncdb'
    run_cmd('%(python)s %(django)s syncdb --noinput')
    print '5. Run wrapper'
    run_cmd('%(python)s %(django)s wrap_runserver')
