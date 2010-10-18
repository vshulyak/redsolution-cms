# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from redsolutioncms.models import ProcessTask
import subprocess
import time
import os, signal
from redsolutioncms.loader import home_dir, process_cmd_string

class Command(BaseCommand):

    def handle(self, *args, **options):
        ProcessTask.objects.create(task=process_cmd_string('"%(django)s" runserver --noreload'))
        self.wrapper()

    def wrapper(self):
        try:
            while True:
#                check executing tasks
                executing_tasks = ProcessTask.objects.filter(
                    executed=True,
                    process_finished=False)
                for task in executing_tasks:
#                    check process finished
                    if os.sys.platform == 'win32':
                        pass
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
                        CREATE_NEW_PROCESS_GROUP = 512
                        p = subprocess.Popen(task.task,
                            creationflags=CREATE_NEW_PROCESS_GROUP)
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
                if task.pid:
                    if os.sys.platform == 'win32':
                        import ctypes
                        CTRL_BREAK_EVENT = 1
                        GenerateConsoleCtrlEvent = ctypes.windll.kernel32.GenerateConsoleCtrlEvent
                        GenerateConsoleCtrlEvent(CTRL_BREAK_EVENT, task.pid)
                    else:
                        try:
                            os.kill(task.pid, signal.SIG_DFL)
                        except OSError:
                            pass
                        else:
                            os.killpg(os.getpgid(task.pid), signal.SIGINT)
                        task.process_finished = True
                        task.save()
            not_executed_tasks = ProcessTask.objects.filter(
                executed=False)
            not_executed_tasks.update(executed=True, process_finished=True)
            raise KeyboardInterrupt

