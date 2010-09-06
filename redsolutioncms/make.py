import os

from redsolutioncms.models import CMSSettings

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

    def __init__(self):
        """
        Create make object.
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
    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to(os.path.join('..', 'buildout.cfg'), 'redsolutioncms/project/buildout.cfg', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'develop.cfg'), 'redsolutioncms/project/develop.cfg', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'bootstrap.py'), 'redsolutioncms/project/bootstrap.py', {}, 'w')
        cms_settings.render_to('__init__.py', 'redsolutioncms/project/__init__.py', {}, 'w')
        cms_settings.render_to('development.py', 'redsolutioncms/project/development.py', {}, 'w')
        cms_settings.render_to('production.py', 'redsolutioncms/project/production.py', {}, 'w')
        cms_settings.render_to('settings.py', 'redsolutioncms/project/settings.py', {}, 'w')
        cms_settings.render_to('urls.py', 'redsolutioncms/project/urls.py', {}, 'w')
        cms_settings.render_to('manage.py', 'redsolutioncms/project/manage.py', {}, 'w')

        cms_settings.render_to(os.path.join('..', 'templates', 'base.html'), 'redsolutioncms/project/templates/base.html', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'templates', '404.html'), 'redsolutioncms/project/templates/404.html', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'templates', '500.html'), 'redsolutioncms/project/templates/500.html', {}, 'w')

        cms_settings.render_to(os.path.join('..', 'media', 'css', 'base.css'), 'redsolutioncms/project/media/css/base.css', {}, 'w')
        cms_settings.render_to(os.path.join('..', 'media', 'css', 'style.css'), 'redsolutioncms/project/media/css/style.css', {}, 'w')

make = Make()
