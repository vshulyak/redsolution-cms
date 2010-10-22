# -*- coding: utf-8 -*-
import os
import shutil
import sys
import subprocess
from os import remove, listdir
from os.path import join, dirname, exists, abspath
from optparse import OptionParser


# Home dir defined here!
if os.sys.platform == 'win32':
    home_dir = join(os.getenv('USERPROFILE'), '.redsolutioncms')
else:
    home_dir = join(os.getenv('HOME'), '.redsolutioncms')
project_dir = os.getcwd()

def install_in_home():
    '''Copy nessesary files to home folder''' 
    # check target dir doesn't exists
    import redsolutioncms
    if exists(home_dir):
        # Delete downloaded libraries
        if exists(join(home_dir, 'eggs')):
            shutil.rmtree(join(home_dir, 'eggs'))
        # Delete all files copied from home
        for filename in listdir(join(dirname(redsolutioncms.__file__), 'home')):
            path = join(home_dir, filename)
            if exists(path):
                remove(path)
        if exists(join(home_dir, 'cms.sqlite')):
            remove(join(home_dir, 'cms.sqlite'))
        # delete *.pyc files
        for filename in listdir(home_dir):
            if '.pyc' in filename:
                remove(join(home_dir, filename))
    else:
        os.mkdir(home_dir)

    for filename in listdir(join(dirname(redsolutioncms.__file__), 'home')):
        src = join(dirname(redsolutioncms.__file__), 'home', filename)
        shutil.copy(src, home_dir)

def run_cmd(cmd, cmd_dict=None):
    # I splitted this function in two for API usage in CMS task system
    cmd = process_cmd_string(cmd, cmd_dict)
    run_in_home(cmd)

def process_cmd_string(cmd, cmd_dict=None):
    if cmd_dict is None:
        cmd_dict = {}
    default_dict = {
        'python': sys.executable,
        'buildout_cfg': join(home_dir, 'buildout.cfg'),
        'bootstrap': join(home_dir, 'bootstrap.py'),
        'buildout': join(home_dir, 'bin', 'buildout'),
        'django': join(home_dir, 'bin', 'django'),
    }
    cmd_dict.update(default_dict)
    return cmd % cmd_dict

def run_in_home(cmd):
    # run python boostrap.py from home installation dir 
    cwd = os.getcwd()
#    os.chdir(home_dir)
    subprocess.call(cmd, shell=(os.sys.platform != 'win32'))
#    os.chdir(cwd)


def main():
    parser = OptionParser()
    parser.add_option('-c', '--continue', action='store_true', dest='continue_install',
        help="Continue installation, doesn't delete old files", default=False)
    parser.add_option('-t', '--test', action='store_true', dest='test',
        help="Test variables", default=False)
    
    (options, args) = parser.parse_args()
    # TODO: Find installed CMS automatically and ask user, does he want to delete old files
    
    if options.test:
        print 'Test mode'
        print 'home_dir=%s' % home_dir
        print 'project_dir=%s' % project_dir
        print process_cmd_string('python: %(python)s')
        print process_cmd_string('buildout_cfg: %(buildout_cfg)s')
        print process_cmd_string('bootstrap: %(bootstrap)s')
        print process_cmd_string('bulidout: %(buildout)s')
        print process_cmd_string('django: %(django)s')
        sys.exit(0)
    
    if not options.continue_install:
        print '1. Copying files to home dir'
        install_in_home()
        print '2. Bootstraping'
        run_cmd('"%(python)s" "%(bootstrap)s" -c "%(buildout_cfg)s"')
        print '3. Building'
        run_cmd('"%(buildout)s" -c "%(buildout_cfg)s"')
    print '4. Syncdb'
    run_cmd('"%(django)s" syncdb --noinput')
    print '5. Run wrapper'
    run_cmd('"%(django)s" wrap_runserver')

if __name__ == '__main__':
    # set path automatically
    sys.path[0:0] = [dirname(dirname(abspath(__file__))),]

    main()
