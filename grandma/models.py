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
    project_name = models.CharField(max_length=50, verbose_name=_('project name'), default='example')
    database_engine = models.CharField(max_length=50, verbose_name=_('database engine'), default='sqlite')
    database_name = models.CharField(max_length=50, verbose_name=_('database name'), default='example.sqlite')
    database_user = models.CharField(max_length=50, verbose_name=_('database user'), default='', blank=True)
    database_password = models.CharField(max_length=50, verbose_name=_('database password'), default='', blank=True)
    database_host = models.CharField(max_length=50, verbose_name=_('database host'), default='', blank=True)
    database_port = models.IntegerField(verbose_name=_('database port'), default=0, blank=True)

class GrandmaInstalledApps(models.Model):
    class Meta:
        unique_together = (
            ('settings', 'name',),
        )
    settings = models.ForeignKey(GrandmaSettings, related_name='installed_apps')
    selected = models.BooleanField(verbose_name=_('Selected'))
    name = models.CharField(verbose_name=_('Module name'), max_length=255)
