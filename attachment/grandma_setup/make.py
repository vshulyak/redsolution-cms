import os
from attachment.grandma_setup.models import AttachmentSettings
from grandma.models import get_last_settings
from grandma.make import BaseMake

class Make(BaseMake):
    def load(self):
        pass

    def before(self):
        pass

    def make(self):
        pass

    def after(self):
        settings = get_last_settings(AttachmentSettings)
        settings_py = os.path.join([self.project_dir, 'settings.py'])
        for_models = ', '.join([model.name for model in settings.for_models])
        link_models = ', '.join([model.name for model in settings.link_models])

        open(settings_py, 'a+').write(
'''# django-tinymce-attachment

INSTALLED_APPS += ['attachment', ]

ATTACHMENT_FOR_MODELS = ['%s']
ATTACHMENT_LINK_MODELS = ['%s']
''' % (for_models, link_models))
