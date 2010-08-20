from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from grandma.forms import GrandmaPackagesForm, UserCreationForm
from grandma.importpath import importpath
from grandma.make import AlreadyMadeException
from grandma.models import GrandmaSettings, GrandmaEntryPoint, \
    GrandmaCreatedModel, ProcessTask
from grandma.packages import search_index, install
from pexpect import TIMEOUT
import os
import pexpect
from django.utils.translation import ugettext_lazy as _

CONFIG_FILES = ['manage', 'settings', 'urls', ]

def list_packages():
    """
    Creates objects in GrandmaPackages model for all modules at PYPI
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    all_packages = search_index('grandma')

    if not grandma_settings.packages.count():
        for package in all_packages:
            grandma_settings.packages.create(
                selected=False,
                package=package['name'],
                version=package['version'],
                verbose_name=package['name'].replace('django-', '').replace('grandma.', ''),
                description=package['summary']
            )

def index(request):
    """
    User can set base settings.
    Shows base settings.
    Saves base settings.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    grandma_settings.initialized = True
    grandma_settings.save()
    grandma_settings_class = modelform_factory(GrandmaSettings, exclude=['grandma_dir', 'project_dir', 'initialized'])
    if request.method == 'POST':
        form = grandma_settings_class(data=request.POST, files=request.FILES, instance=grandma_settings)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = grandma_settings_class(instance=grandma_settings)
    return render_to_response('grandma/index.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def apps(request):
    """
    User can select packages.
    Fetches list of available packages. 
    Saves settings.
    """
    list_packages()
    if request.method == 'POST':
        form = GrandmaPackagesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('load'))
    else:
        form = GrandmaPackagesForm()
    return render_to_response('grandma/apps.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def load(request):
    """
    User can wait.
    Fetches packages. 
    Saves installation information for packages.
    Makes settings.py, urls.py, manage.py with installed setup-packages.
    Syncdb for setup-packages.
    """
    task = ProcessTask.objects.create(task='bin/django kill_runserver',
        lock=True, wait=True)
    ProcessTask.objects.create(task='bin/django install_packages', wait=True)
    ProcessTask.objects.create(task='bin/django change_settings', wait=True)
    ProcessTask.objects.create(task='python grandma/manage.py syncdb', wait=True)
    ProcessTask.objects.create(task='python grandma/manage.py runserver')
    return render_to_response('grandma/wait.html', {
        'task_id':task.id, 'redirect_to': reverse('custom'),
        'start_task_id':task.id,
    }, context_instance=RequestContext(request))

def restart(request):
    """
    User can`t see it. It will be called by javascript.
    Rewrite manage.py for current server, so server will be restarted.
    """
    task = ProcessTask.objects.create(task='bin/django kill_runserver',
        lock=True, wait=True)
    ProcessTask.objects.create(task='bin/django install_packages', wait=True)
    ProcessTask.objects.create(task='bin/django change_settings', wait=True)
    ProcessTask.objects.create(task='python grandma/manage.py syncdb', wait=True)
    ProcessTask.objects.create(task='python grandma/manage.py runserver')
    task.lock = False
    task.save()
    return HttpResponse()

def started(request, task_id):
    """
    User can`t see it. It will be called by javascript.
    Used to check, whether server is available after restart.
    """
    task = ProcessTask.objects.get(id=task_id)
    if task.process_finished:
        return HttpResponse()

def custom(request):
    """
    User can go to detail settings for packages or can ask to make project.
    Make files for new project.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        entry_points = ['grandma']
        grandma_settings.head_blocks.all().delete()
        grandma_settings.top_blocks.all().delete()
        grandma_settings.left_blocks.all().delete()
        grandma_settings.center_blocks.all().delete()
        grandma_settings.right_blocks.all().delete()
        grandma_settings.bottom_blocks.all().delete()
        for package in grandma_settings.packages.installed():
            for entry_point in package.entry_points.all():
                entry_points.append(entry_point.module)
        make_objects = []
        for entry_point in entry_points:
            try:
                make_class = importpath('.'.join([entry_point, 'make', 'Make']))
            except ImportError:
                continue
            make_objects.append(make_class())
        for make_object in make_objects:
            try:
                make_object.premake()
            except AlreadyMadeException:
                pass
        for make_object in make_objects:
            try:
                make_object.make()
            except AlreadyMadeException:
                pass
        for make_object in make_objects:
            try:
                make_object.postmake()
            except AlreadyMadeException:
                pass
        return HttpResponseRedirect(reverse('build'))
    return render_to_response('grandma/custom.html', {
        'grandma_settings': grandma_settings,
    }, context_instance=RequestContext(request))

def cancel_lock(request, task_id):
    task = ProcessTask.objects.get(id=task_id)
    task.lock = False
    task.save()
    return HttpResponse()

def build(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    task = ProcessTask.objects.create(task='bin/django kill_runserver',
        lock=True, wait=True)
    bootstrap_name = os.path.join(grandma_settings.project_dir, 'bootstrap.py')
    buildout_cfg_name = os.path.join(grandma_settings.project_dir, 'buildout.cfg')
    ProcessTask.objects.create(
        task='python %s -c %s' % (bootstrap_name, buildout_cfg_name),
        wait=True)
    buildout_name = os.path.join(grandma_settings.project_dir, 'bin', 'buildout')
    ProcessTask.objects.create(
        task='python %s -c %s' % (buildout_name, buildout_cfg_name), wait=True)
    django_name = os.path.join(grandma_settings.project_dir, 'bin', 'django')
    ProcessTask.objects.create(
        task='python %s syncdb --noinput' % django_name, wait=True)
    ProcessTask.objects.create(
        task='python %s runserver 127.0.0.1:8001' % django_name)
    ProcessTask.objects.create(task='bin/django runserver')

    return render_to_response('grandma/wait.html',
        {'task_id': task.id, 'redirect_to': reverse('create_superuser'),
            'start_task_id':task.id},
         context_instance=RequestContext(request))


def create_superuser(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            django_name = os.path.join(grandma_settings.project_dir, 'bin', 'django')
            child = pexpect.spawn('python %s createsuperuser' % django_name,
                timeout=3)
            child.expect("Username.*")
            child.sendline(form.cleaned_data['username'])
            try:
                child.expect("E-mail.*")
            except TIMEOUT:
                from django import forms
                form.errors['username'] = [_('This username is busy.')]
            else:
#                child.expect("E-mail.*")
                child.sendline(form.cleaned_data['email'])
                child.expect("Password.*")
                child.sendline(form.cleaned_data['password1'])
                child.expect("Password.*")
                child.sendline(form.cleaned_data['password1'])
                child.expect("Superuser.*")
                return HttpResponseRedirect(reverse('done'))
    else:
        form = UserCreationForm()
    return render_to_response('grandma/build.html', {
        'grandma_settings': grandma_settings,
        'bootstrap': os.path.join(grandma_settings.project_dir, 'bootstrap.py'),
        'buildout': os.path.join(grandma_settings.project_dir, 'bin', 'buildout'),
        'django': os.path.join(grandma_settings.project_dir, 'bin', 'django'),
        'form': form,
    }, context_instance=RequestContext(request))

def done(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    return render_to_response('grandma/done.html', {
        'grandma_settings': grandma_settings,
        'django': os.path.join(grandma_settings.project_dir, 'bin', 'django'),
    }, context_instance=RequestContext(request))
