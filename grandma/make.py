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
            self.premake()
            self.premade = True

    def make(self):
        """
        Call it to make project for this application.
        """
        if not self.made:
            self.make()
            self.made = True

    def postmake(self):
        """
        Call it after project was made for this application.
        """
        if not self.postmade:
            self.postmake()
            self.postmade = True

    def _premake(self):
        """
        Called immediately before make project for this application.
        You can override it.
        """

    def _make(self):
        """
        Called to make project for this application.
        """

    def _postmake(self):
        """
        Called after project was made for this application.
        """

class Make(BaseMake):
    def make(self):
        grandma_settings = GrandmaSettings.objects.get_settings()
        data = render_to_string('grandma/buildout.cfg', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to(os.path.join('..', 'buildout.cfg'), data)
        data = render_to_string('grandma/develop.cfg', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to(os.path.join('..', 'develop.cfg'), data)
        # bootstrap
        grandma_settings.append_to('__init__.py', '')
        data = render_to_string('grandma/development.py', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to('development.py', data)
        data = render_to_string('grandma/production.py', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to('production.py', data)
        data = render_to_string('grandma/settings.py', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to('settings.py', data)
        data = render_to_string('grandma/urls.py', {
            'grandma_settings': grandma_settings,
        })
        grandma_settings.append_to('urls.py', data)

def make():
    """
    Make project.
    """
    make_objects = []
    for application in ['grandma'] + settings.GRANDMA_APPS:
        try:
            make_class = importpath('.'.join([application, 'make', 'Make']), 'Making project')
        except ImproperlyConfigured:
            continue
        make_objects.append(make_class())
    for make_object in make_objects:
        make_object.premake()
    for make_object in make_objects:
        make_object.make()
    for make_object in make_objects:
        make_object.postmake()
