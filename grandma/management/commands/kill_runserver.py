# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from grandma.models import ProcessTask
import time
import os, signal, sys

class Command(BaseCommand):

    def handle(self, *args, **options):
        runserver_tasks = ProcessTask.objects.filter(process_finished=False,
            task__contains=' runserver', executed=True)
        for task in runserver_tasks:
            if task.pid:
                try:
                    os.kill(task.pid, signal.SIG_DFL)
                except OSError:
                    pass
                else:
                    sys.stdout.flush()
                    os.killpg(os.getpgid(task.pid), signal.SIGINT)
                task.process_finished = True
                task.save()
