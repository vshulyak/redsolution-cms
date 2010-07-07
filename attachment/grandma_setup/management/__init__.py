from django.db.models.signals import post_syncdb
from grandma.models import GrandmaSettings, get_last_settings
from grandma_setup import models
from grandma_setup.models import AttachmentSettings, AttachmentLinkModels, AttachmentForModels

def content_save(sender, **kwargs):
    if kwargs['verbosity']:
        print 'Populate %s with initial data' % sender
    settings = AttachmentSettings.objects.create()
    grandma_settings = get_last_settings(GrandmaSettings)
    for app in grandma_settings.installed_apps.all():
        if app == 'grandma_plugins_easy_news':
            AttachmentForModels.objects.create(settings=settings, model='easy_news.models.News')
            AttachmentLinkModels.objects.create(settings=settings, model='easy_news.models.News')
        if app == 'grandma_plugins_pages_cms':
            AttachmentForModels.objects.create(settings=settings, model='pages.models.Page')
            AttachmentLinkModels.objects.create(settings=settings, model='pages.models.Page')

post_syncdb.connect(content_save, sender=models)

