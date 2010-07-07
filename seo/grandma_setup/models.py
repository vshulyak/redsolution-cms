from django.utils import simplejson

class Settings:
    FILE_NAME = 'settings.json'

    def __init__(self):
        data = simplejson.load(open(self.FILE_NAME))
        self.seo_for_models = getattr(data, 'seo_for_models', [])

    def save(self):
        data = {
            'seo_for_models': self.seo_for_models,
        }
        simplejson.dumps(data, open(self.FILE_NAME, 'w'))
