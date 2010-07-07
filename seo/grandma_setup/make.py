import os
from models import Settings
from grandma.make import BaseMake

class Make(BaseMake):
    def before(self):
        pass

    def make(self):
        pass

    def after(self):
        settings = Settings()
        settings_py = os.path.join([self.project_dir, 'settings.py'])
        open(settings_py, 'a+').write(
'''# django-seo

INSTALLED_APPS += ['seo', ]

SEO_FOR_MODELS = ['%s', ]
''' % settings.seo_for_models)
