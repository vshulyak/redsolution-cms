from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from grandma.importpath import importpath

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
        pass

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
        if not make_object.premade:
            make_object.premake()
            make_object.premade = True
    for make_object in make_objects:
        if not make_object.made:
            make_object.make()
            make_object.made = True
    for make_object in make_objects:
        if not make_object.postmade:
            make_object.postmake()
            make_object.postmade = True
