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
        pass
