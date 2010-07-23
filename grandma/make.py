import os

from grandma.models import GrandmaSettings

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
        grandma_settings = GrandmaSettings.objects.get_settings()
        grandma_settings.render_to(os.path.join('..', 'buildout.cfg'), 'grandma/project/buildout.cfg', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'develop.cfg'), 'grandma/project/develop.cfg', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'bootstrap.py'), 'grandma/project/bootstrap.py', {}, 'w')
        grandma_settings.render_to('__init__.py', 'grandma/project/__init__.py', {}, 'w')
        grandma_settings.render_to('settings.py', 'grandma/project/settings.py', {}, 'w')
        grandma_settings.render_to('urls.py', 'grandma/project/urls.py', {}, 'w')
        grandma_settings.render_to('manage.py', 'grandma/project/manage.py', {}, 'w')

        grandma_settings.render_to(os.path.join('..', 'templates', 'base.html'), 'grandma/templates/base.html', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'templates', '404.html'), 'grandma/templates/404.html', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'templates', '500.html'), 'grandma/templates/500.html', {}, 'w')

        grandma_settings.render_to(os.path.join('..', 'media', 'css', 'base.css'), 'grandma/media/css/base.css', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'media', 'css', 'style.css'), 'grandma/media/css/style.css', {}, 'w')

make = Make()
