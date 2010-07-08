# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

class BaseSettings(models.Model):
    class Meta:
        abstract = True
    created = models.DateTimeField(default=datetime.datetime.now)

def get_last_settings(model):
    try:
        return model.objects.latest('created')
    except ObjectDoesNotExist:
        return model()

class GrandmaSettings(BaseSettings):
    project_name = models.CharField(max_length=50, verbose_name=_('Project name'), default='example')
    database_engine = models.CharField(max_length=50, verbose_name=_('Database engine'), default='sqlite')
    database_name = models.CharField(max_length=50, verbose_name=_('Database name'), default='example.sqlite')
    database_user = models.CharField(max_length=50, verbose_name=_('Database user'), default='', blank=True)
    database_password = models.CharField(max_length=50, verbose_name=_('Database password'), default='', blank=True)
    database_host = models.CharField(max_length=50, verbose_name=_('Database host'), default='localhost', blank=True)
    database_port = models.IntegerField(verbose_name=_('Database port'), default=5432, blank=True)

class GrandmaApplication(models.Model):
    class Meta:
        unique_together = (
            ('settings', 'name',),
        )
    settings = models.ForeignKey(GrandmaSettings, related_name='applications')
    application = models.CharField(verbose_name=_('Application'), max_length=255)
    install = models.BooleanField(verbose_name=_('Install'))

def get_grandma_settings():
    grandma_settings = get_last_settings(GrandmaSettings)
    grandma_settings.save()
    return grandma_settings
