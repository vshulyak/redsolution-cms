# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class SettingsManager(models.Manager):
    def get_settings(self):
        if self.get_query_set().count():
            return self.get_query_set()[0]
        else:
            self.get_query_set().create()

class BaseSettings(models.Model):
    class Meta:
        abstract = True
    objects = SettingsManager()

class GrandmaSettings(BaseSettings):
    project_name = models.CharField(max_length=50, verbose_name=_('Project name'), default='example')
    database_engine = models.CharField(max_length=50, verbose_name=_('Database engine'), default='sqlite')
    database_name = models.CharField(max_length=50, verbose_name=_('Database name'), default='example.sqlite')
    database_user = models.CharField(max_length=50, verbose_name=_('Database user'), default='', blank=True)
    database_password = models.CharField(max_length=50, verbose_name=_('Database password'), default='', blank=True)
    database_host = models.CharField(max_length=50, verbose_name=_('Database host'), default='localhost', blank=True)
    database_port = models.IntegerField(verbose_name=_('Database port'), default=5432, blank=True, null=True)

class GrandmaApplication(models.Model):
    class Meta:
        unique_together = (
            ('settings', 'package',),
        )
    settings = models.ForeignKey(GrandmaSettings, related_name='applications')
    install = models.BooleanField(verbose_name=_('Install'))
    package = models.CharField(verbose_name=_('Package'), max_length=255)
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    description = models.TextField(verbose_name=_('Name'))
