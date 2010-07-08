import os
import subprocess
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from grandma.importpath import importpath
from grandma.models import get_grandma_settings
from grandma.forms import GrandmaSettingsForm



def list_applications():
    """
    Load list of available application.
    """
    return [
        'grandma_plugins_django_pages_cms',
        'grandma_plugins_django_easy_news',
        'grandma_plugins_django_config',
        'grandma_plugins_django_tinymce',
        'grandma_plugins_django_tinymce_attachment',
        'grandma_plugins_django_seo',
        'grandma_plugins_django_hex_storage',
        'grandma_plugins_django_chunks',
        'grandma_plugins_django_trusted_html',
        'grandma_plugins_django_model_urls',
        'grandma_plugins_django_url_methods',
        'grandma_plugins_django_menu_proxy',
        'grandma_plugins_django_imagekit',
    ]

def list_recommended():
    """
    Load list of recommended application.
    """
    return [
        'grandma_plugins_django_pages_cms',
        'grandma_plugins_django_easy_news',
        'grandma_plugins_django_config',
        'grandma_plugins_django_tinymce',
        'grandma_plugins_django_tinymce_attachment',
        'grandma_plugins_django_hex_storage',
        'grandma_plugins_django_menu_proxy',
        'grandma_plugins_django_imagekit',
    ]

def load_application(name):
    """
    Load application with specified name.
    Return path to the application or None if loading failed.
    """
    return os.path.abspath(os.path.join('setup_eggs', name))

def find_grandma_setups(path):
    """
    Search for grandma setups in path.
    Return list of python-paths to grandma_setup modules.
    """
    name = os.path.basename(path)
    app = '_'.join(name.slit('_')[3:])
    return ['.'.join(name, app, 'grandma_setup')]

def check_grandma_setup(module):
    """
    Try to check grandma setup module.
    Return true to module can be imported.
    """
    try:
        importpath(module, 'check')
    except ImproperlyConfigured:
        return False
    else:
        return True

def load_applications():
    """
    Load applications.
    Return tuple:
    * list of paths to be imported
    * list of grandma setup modules
    """
    paths = []
    modules = []
    grandma_settings = get_grandma_settings()
    for application in grandma_settings.applications.filter(install=True):
        path = load_application(application.application)
        if path is not None:
            setups = find_grandma_setups(path)
            for setup in setups:
                if check_grandma_setup(setup):
                    modules.append(setup)
            paths.append(path)
    return paths, modules

def load():
    """
    Load applications, syncdb and run news server.
    """
    paths, modules = load_applications()
    open('manage_apps.py').write(
        render_to_string('grandma/manage_apps.py', {
            'paths': paths,
        })
    )
    open('settings_apps.py').write(
        render_to_string('grandma/settings_apps.py', {
            'modules': modules,
        })
    )
    subprocess.Popen('python manage_apps.py syncdb').wait()
    subprocess.Popen('python manage_apps.py runserver 127.0.0.1:8001').wait()

def index(request):
    grandma_settings = get_grandma_settings()
    if request.method == 'POST':
        form = GrandmaSettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = GrandmaSettingsForm(instance=grandma_settings)
    return render_to_response('grandma/index.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def apps(request):
    grandma_settings = get_grandma_settings()
    applications = list_applications()
    recommended = list_recommended()
    for application in applications:
        grandma_settings.applications.add(application=application, install=application in recommended)


    if request.method == 'POST':
        form = GrandmaSettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = GrandmaSettingsForm(instance=settings)
    return render_to_response('grandma/apps.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def custom(request):
    return HttpResponse()

def build(request):
    return HttpResponse()

def done(request):
    return HttpResponse()


