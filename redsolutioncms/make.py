import os

from redsolutioncms.models import CMSSettings
from django.conf import settings
from random import choice


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

    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(['..', 'buildout.cfg'], 'redsolutioncms/project/buildout.cfg',
            {'index': getattr(settings, 'CUSTOM_PACKAGE_INDEX', None)}, 'w')
        cms_settings.render_to(['..', 'develop.cfg'], 'redsolutioncms/project/develop.cfg', {}, 'w')
        cms_settings.render_to(['..', 'bootstrap.py'], 'redsolutioncms/project/bootstrap.pyt', {}, 'w')
        cms_settings.render_to('__init__.py', 'redsolutioncms/project/__init__.pyt', {}, 'w')
        cms_settings.render_to('development.py', 'redsolutioncms/project/development.pyt', {}, 'w')
        cms_settings.render_to('production.py', 'redsolutioncms/project/production.pyt', {}, 'w')
        cms_settings.render_to('settings.py', 'redsolutioncms/project/settings.pyt', {
            'secret': ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        }, 'w')
        cms_settings.render_to('urls.py', 'redsolutioncms/project/urls.pyt', {}, 'w')
        cms_settings.render_to('manage.py', 'redsolutioncms/project/manage.pyt', {}, 'w')
        # TODO: Add .gitignore

        cms_settings.render_to(os.path.join('..', 'templates', '404.html'), 'redsolutioncms/project/templates/404.html', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'templates', '500.html'), 'redsolutioncms/project/templates/500.html', {}, 'w')

        cms_settings.render_to(os.path.join('..', 'media', 'css', 'base.css'), 'redsolutioncms/project/media/css/base.css', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'media', 'css', 'style.css'), 'redsolutioncms/project/media/css/style.css', {}, 'w')

    def postmake(self):
        super(Make, self).postmake()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(os.path.join('..', 'templates', 'base.html'), 'redsolutioncms/project/templates/base.html', {}, 'w')

make = Make()
