# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from redsolutioncms.models import CMSSettings, ProcessTask
import time
import os, signal, sys
from django.conf import settings
from django.template.loader import render_to_string

CONFIG_FILES = ['manage', 'settings', 'urls', ]

class Command(BaseCommand):

    def handle(self, *args, **options):
        cms_settings = CMSSettings.objects.get_settings()
        for file_name in CONFIG_FILES:
            data = render_to_string('redsolutioncms/%s.py' % (file_name), {
                'cms_settings': cms_settings,
            })
            open(os.path.join(cms_settings.cms_dir,
                '%s_additional.py' % (file_name)), 'w').write(data)
