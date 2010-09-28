# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from redsolutioncms.loader import home_dir
from redsolutioncms.models import CMSSettings, ProcessTask
import os
import signal
import sys
import time

CONFIG_FILES = ['extrapath', 'settings', 'urls', ]

class Command(BaseCommand):

    def handle(self, *args, **options):
        cms_settings = CMSSettings.objects.get_settings()
        for file_name in CONFIG_FILES:
            data = render_to_string('redsolutioncms/%s.pyt' % (file_name), {
                'cms_settings': cms_settings,
            })
            open(os.path.join(home_dir,
                '%s_additional.py' % (file_name)), 'w').write(data)
