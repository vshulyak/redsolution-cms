from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from grandma.importpath import importpath
from grandma.models import GrandmaSettings
from django.template.loader import render_to_string
import os

class BaseMake():
    def __init__(self):
        """
        Create make object.
        """
        self.premade = False
        self.made = False
        self.postmade = False

    def premake(self):
        """
        Call it immediately before make project for this application.
        """
        if not self.premade:
            self._premake()
            self.premade = True

    def make(self):
        """
        Call it to make project for this application.
        """
        if not self.made:
            self._make()
            self.made = True

    def postmake(self):
        """
        Call it after project was made for this application.
        """
        if not self.postmade:
            self._postmake()
            self.postmade = True

    def _premake(self):
        """
        Called immediately before make project for this application.
        You can override it.
        """

    def _make(self):
        """
        Called to make project for this application.
        You can override it.
        """

    def _postmake(self):
        """
        Called after project was made for this application.
        You can override it.
        """

class Make(BaseMake):
    def make(self):
        grandma_settings = GrandmaSettings.objects.get_settings()
        grandma_settings.render_to(os.path.join('..', 'buildout.cfg'), 'grandma/buildout.cfg', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'develop.cfg'), 'grandma/develop.cfg', {}, 'w')
        grandma_settings.render_to(os.path.join('..', 'bootstrap.py'), 'grandma/bootstrap.py', {}, 'w')
        grandma_settings.render_to('__init__.py', 'grandma/__init__.py', {}, 'w')
        grandma_settings.render_to('development.py', 'grandma/development.py', {}, 'w')
        grandma_settings.render_to('production.py', 'grandma/production.py', {}, 'w')
        grandma_settings.render_to('settings.py', 'grandma/settings.py', {}, 'w')
        grandma_settings.render_to('urls.py', 'grandma/urls.py', {}, 'w')
        grandma_settings.render_to('manage.py', 'grandma/manage_apps.py', {}, 'w')
