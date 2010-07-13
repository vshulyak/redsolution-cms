# -*- coding: utf-8 -*-

import os
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

class BaseSettingsManager(models.Manager):
    def get_settings(self):
        if self.get_query_set().count():
            return self.get_query_set()[0]
        else:
            self.get_query_set().create()

class BaseSettings(models.Model):
    class Meta:
        abstract = True
    objects = BaseSettingsManager()

class GrandmaSettings(BaseSettings):
    DATABASE_ENGINES = [
        ('postgresql_psycopg2', 'postgresql_psycopg2',),
        ('postgresql', 'postgresql',),
        ('mysql', 'mysql',),
        ('sqlite3', 'sqlite3',),
        ('oracle', 'oracle',),
    ]

    project_path = models.CharField(verbose_name=_('Project path'), max_length=255, default=lambda: os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    project_name = models.CharField(verbose_name=_('Project name'), max_length=50, default='example')
    database_engine = models.CharField(verbose_name=_('Database engine'), max_length=50, choices=DATABASE_ENGINES, default='sqlite3')
    database_name = models.CharField(verbose_name=_('Database name'), max_length=50, default='example.sqlite')
    database_user = models.CharField(verbose_name=_('Database user'), max_length=50, blank=True, default='')
    database_password = models.CharField(verbose_name=_('Database password'), max_length=50, blank=True, default='')
    database_host = models.CharField(verbose_name=_('Database host'), max_length=50, blank=True, default='')
    database_port = models.IntegerField(verbose_name=_('Database port'), blank=True, null=True)

    def render_to(self, file_name, template_name, dictionary={}, mode='a+'):
        file_name = os.path.join(self.project_path, self.project_name, file_name)
        dictionary['grandma_settings'] = self
        open(file_name, mode).write(render_to_string(template_name, dictionary))

    def package_was_installed(self, package_name):
        try:
            return self.packages.get(package=package_name).ok
        except ObjectDoesNotExist:
            return False

class GrandmaPackage(models.Model):
    class Meta:
        unique_together = (
            ('settings', 'package',),
        )
    settings = models.ForeignKey(GrandmaSettings, related_name='packages')

    selected = models.BooleanField(verbose_name=_('Selected'))
    package = models.CharField(verbose_name=_('Package'), max_length=255)
    version = models.CharField(verbose_name=_('Package version'), max_length=50)
    verbose_name = models.CharField(verbose_name=_('Verbose name'), max_length=255)
    description = models.TextField(verbose_name=_('Description'))
    path = models.CharField(verbose_name=_('Installed to path'), max_length=255, blank=True, null=True)
    ok = models.BooleanField(verbose_name=_('Download OK'), default=False)

    def __unicode__(self):
        return self.package

class GrandmaEntryPoint(models.Model):
    package = models.ForeignKey(GrandmaPackage, related_name='entry_points')
    module = models.CharField(verbose_name=_('Module name'), max_length=255)
    has_urls = models.BooleanField(verbose_name=_('Has urls'))

    def __unicode__(self):
        return 'Entry point %s' % self.module
