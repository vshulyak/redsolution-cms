import os

from redsolutioncms.models import CMSSettings
from django.conf import settings
from random import choice
from redsolutioncms.utils import prepare_fixtures
from redsolutioncms.loader import project_dir

class AlreadyMadeException(Exception):
    """
    Exception raise if function in Make class was called twice.
    """

class BaseMake(object):
    """
    Base class for all Make classes.
    You MUST call super method before any action in overridden functions.
    Functions can raise ``AlreadyMadeException`` if function was already called. 
    """
    # In customizing apps view user has selected frontpage handler.
    # this variable can be set to True in that view

    def __init__(self):
        """
        Create make object.
        """
        self.flush()

    def flush(self):
        """
        Flush all flags as if project was not made yet. 
        """
        self.premade = False
        self.made = False
        self.postmade = False

    def premake(self):
        """
        Called immediately before make() for all packages.
        """
        if self.premade:
            raise AlreadyMadeException
        self.premade = True

    def make(self):
        """
        Called to make() settings for this package.
        """
        if self.made:
            raise AlreadyMadeException
        self.made = True

    def postmake(self):
        """
        Called after all make() for all packages.
        """
        if self.postmade:
            raise AlreadyMadeException
        self.postmade = True

class Make(BaseMake):
    def premake(self):
        super(Make, self).premake()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(os.path.join('..', 'templates', 'base_template.html'), 'redsolutioncms/project/templates/base_template.html', {}, 'w')
        # reset initial data fixture
        initial_data_filename = os.path.join(project_dir, 'fixtures', 'initial_data.json')
        if os.path.exists(initial_data_filename):
            os.remove(initial_data_filename)

    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(['..', 'buildout.cfg'], 'redsolutioncms/project/buildout.cfg',
            {'index': getattr(settings, 'CUSTOM_PACKAGE_INDEX', None)}, 'w')
        cms_settings.render_to('development.py', 'redsolutioncms/project/development.pyt', {}, 'w')
        cms_settings.render_to('production.py', 'redsolutioncms/project/production.pyt', {}, 'w')
        cms_settings.render_to('settings.py', 'redsolutioncms/project/settings.pyt', {
            'secret': ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        }, 'w')
        cms_settings.render_to('urls.py', 'redsolutioncms/project/urls.pyt', {}, 'w')
        cms_settings.render_to('manage.py', 'redsolutioncms/project/manage.pyt', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'templates', '404.html'), 'redsolutioncms/project/templates/404.html', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'templates', '500.html'), 'redsolutioncms/project/templates/500.html', {}, 'w')
#===============================================================================
# Static templates
#===============================================================================
        redsolutioncms_templates_dir = os.path.join(os.path.dirname(__file__),
            'templates', 'redsolutioncms', 'project')

        cms_settings.copy_to(
            os.path.join(cms_settings.project_dir, 'develop.cfg',),
            os.path.join(redsolutioncms_templates_dir, 'develop.cfg'),
        )
        cms_settings.copy_to(
            os.path.join(cms_settings.project_dir, 'bootstrap.py',),
            os.path.join(redsolutioncms_templates_dir, 'bootstrap.pyt'),
        )
        cms_settings.copy_to(
            os.path.join(cms_settings.project_dir, '.gitignore',),
            os.path.join(redsolutioncms_templates_dir, 'gitignore'),
        )
        cms_settings.copy_to(
            os.path.join(cms_settings.project_dir, cms_settings.project_name, '__init__.py',),
            os.path.join(redsolutioncms_templates_dir, '__init__.pyt'),
        )
        cms_settings.copy_to(
            os.path.join(cms_settings.project_dir, 'media'),
            os.path.join(redsolutioncms_templates_dir, 'media'),
            merge=True
        )

    def postmake(self):
        super(Make, self).postmake()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(os.path.join('..', 'templates', 'base.html'), 'redsolutioncms/project/templates/base.html', {}, 'w')
        cms_settings.render_to('urls.py', 'redsolutioncms/project/sitemaps.pyt')
        
        # process initial data
        initial_data_filename = os.path.join(project_dir, 'fixtures', 'initial_data.json')
        if os.path.exists(initial_data_filename):
            content = open(initial_data_filename).read()
        fixture_data = prepare_fixtures(content)
        cms_settings.render_to(['..', 'fixtures', 'initial_data.json'],
            'redsolutioncms/project/raw_content.txt', {'content': fixture_data}, 'w')        

make = Make()
