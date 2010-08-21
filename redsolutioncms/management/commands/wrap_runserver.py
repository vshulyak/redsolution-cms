# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from redsolutioncms.models import ProcessTask
import subprocess
import time
import os, signal

class Command(BaseCommand):

    def handle(self, *args, **options):
        ProcessTask.objects.create(task='python redsolutioncms/manage.py runserver')
        self.wrapper()

    def wrapper(self):
        try:
            while True:
#                check executing tasks
                executing_tasks = ProcessTask.objects.filter(
                    executed=True,
                    process_finished=False)
                for task in executing_tasks:
                    try:
                        os.kill(task.pid, signal.SIG_DFL)
                    except OSError:
                        task.process_finished = True
                        task.save()
                tasks = ProcessTask.objects.filter(executed=False)
                time.sleep(1)
                lock_tasks = tasks.filter(lock=True)
                if lock_tasks:
                    first_lock_task = lock_tasks[0]
                    tasks = tasks.filter(id__lt=first_lock_task.id)
                if tasks:
                    task = tasks[0]
                    print task.task, 'executing...'
                    p = subprocess.Popen(task.task, close_fds=True,
                        shell=os.sys.platform != 'win32', preexec_fn=os.setsid,)
                    task.pid = p.pid
                    if task.wait:
                        p.wait()
                        task.process_finished = True
                    task.executed = True
                    task.save()
        except KeyboardInterrupt:
            executing_tasks = ProcessTask.objects.filter(process_finished=False)
            for task in executing_tasks:
                try:
                    os.kill(task.pid, signal.SIG_DFL)
                except OSError:
                    task.process_finished = True
                    task.save()
                else:
                    os.killpg(os.getpgid(task.pid), signal.SIGINT)
            raise KeyboardInterrupt

