# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from grandma.models import GrandmaSettings, ProcessTask
import time
import os, signal, sys
from django.conf import settings
from django.template.loader import render_to_string

CONFIG_FILES = ['manage', 'settings', 'urls', ]

class Command(BaseCommand):

    def handle(self, *args, **options):
        grandma_settings = GrandmaSettings.objects.get_settings()
        for file_name in CONFIG_FILES:
            data = render_to_string('grandma/%s.py' % (file_name), {
                'grandma_settings': grandma_settings,
            })
            open(os.path.join(grandma_settings.grandma_dir,
                '%s_additional.py' % (file_name)), 'w').write(data)
