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
                    if os.sys.platform == 'win32':
                        import ctypes
                        PROCESS_TERMINATE = 1
                        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, task.pid)
                        ctypes.windll.kernel32.TerminateProcess(handle, -1)
                        ctypes.windll.kernel32.CloseHandle(handle)
                    else:
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
                    if os.sys.platform == 'win32':
                        p = subprocess.Popen(task.task, shell=False)
                    else:
                        p = subprocess.Popen(task.task, close_fds=True,
                            shell=True, preexec_fn=os.setsid,)
                    task.pid = p.pid
                    if task.wait:
                        p.wait()
                        task.process_finished = True
                    task.executed = True
                    task.save()
        except KeyboardInterrupt:
            executing_tasks = ProcessTask.objects.filter(process_finished=False)
            for task in executing_tasks:
                if os.sys.platform == 'win32':
                    import ctypes
                    PROCESS_TERMINATE = 1
                    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, task.pid)
                    ctypes.windll.kernel32.TerminateProcess(handle, -1)
                    ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    try:
                        os.kill(task.pid, signal.SIG_DFL)
                    except OSError:
                        task.process_finished = True
                        task.save()
                    else:
                        os.killpg(os.getpgid(task.pid), signal.SIGINT)
            raise KeyboardInterrupt

