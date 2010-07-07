# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from grandma.models import BaseSettings

class AttachmentSettings(BaseSettings):
    pass

class AttachmentForModels(models.Model):
    settings = models.ForeignKey(AttachmentSettings, related_name='for_models')
    model = models.CharField(verbose_name=_('for models'), max_length=255)

class AttachmentLinkModels(models.Model):
    settings = models.ForeignKey(AttachmentSettings, related_name='link_models')
    model = models.CharField(verbose_name=_('link models'), max_length=255)
