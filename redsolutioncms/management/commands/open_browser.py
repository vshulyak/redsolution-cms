# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
import webbrowser, time


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', action='store', type='string',
            dest='url', default='http://localhost:8000'),
        make_option('-d', '--delay', action='store', type='int',
            dest='delay', default=3),
    )
    help = 'Opens browser with a given delay'

    def handle(self, *args, **options):
        time.sleep(options['delay'])
        webbrowser.open_new(options['url'])
