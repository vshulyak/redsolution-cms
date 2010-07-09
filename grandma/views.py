import os
import sys
import random
import subprocess
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from grandma.importpath import importpath
from grandma.models import GrandmaSettings, GrandmaApplication, GrandmaSetup
from grandma.forms import GrandmaApplicationsForm

#'grandma_plugins_django_pages_cms',
#'grandma_plugins_django_easy_news',
#'grandma_plugins_django_config',
#'grandma_plugins_django_tinymce',
#'grandma_plugins_django_tinymce_attachment',
#'grandma_plugins_django_seo',
#'grandma_plugins_django_hex_storage',
#'grandma_plugins_django_chunks',
#'grandma_plugins_django_trusted_html',
#'grandma_plugins_django_model_urls',
#'grandma_plugins_django_url_methods',
#'grandma_plugins_django_menu_proxy',
#'grandma_plugins_django_imagekit',

def list_applications():
    """
    List applications.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    if not grandma_settings.applications.count():
        for package in [
            'django-attachment',
            'django-config',
            'django-seo',
        ]:
            grandma_settings.applications.create(
                selected=False, package=package,
                verbose_name=package.replace('django-', ''),
                description='Description for %s' % package)

def load_application(package):
    """
    Load application with specified name.
    Return path to the application or None if loading failed.
    """
    grandma_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(grandma_dir, '..', 'parts', package))

def find_setups(package):
    """
    Find entry point in package for grandma_setup.
    """
    return [package.replace('django-', '') + '.grandma_setup']

def load_applications():
    """
    Load applications.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    GrandmaSetup.objects.all().delete()
    for application in grandma_settings.applications.filter(selected=True):
        application.path = load_application(application.package)
        application.save()
    for application in grandma_settings.applications.exclude(path=None):
        sys.path.append(application.path)
    for application in grandma_settings.applications.exclude(path=None):
        for module in find_setups(application.package):
            try:
                importpath(module)
            except ImportError:
                continue
            try:
                importpath(module + '.urls')
            except ImportError:
                has_view = False
            else:
                has_view = True
            GrandmaSetup.objects.create(
                application=application, module=module, has_view=has_view)

def index(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    grandma_settings_class = modelform_factory(GrandmaSettings, exclude=['project_path'])
    if request.method == 'POST':
        form = grandma_settings_class(data=request.POST, files=request.FILES, instance=grandma_settings)
        if form.is_valid():
            form.save(commit=True)
#            GrandmaApplication.objects.filter(settings=grandma_settings).delete()
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = grandma_settings_class(instance=grandma_settings)
    return render_to_response('grandma/index.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def apps(request):
    list_applications()
    if request.method == 'POST':
        form = GrandmaApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            load_applications()
            grandma_settings = GrandmaSettings.objects.get_settings()
            grandma_dir = os.path.dirname(os.path.abspath(__file__))
            hash = '%08x' % random.randint(0, 0x100000000)
            for file_name in ['manage_%s.py', 'settings_%s.py', 'urls_%s.py', ]:
                data = render_to_string('grandma/%s' % (file_name % 'apps'), {
                    'grandma_settings': grandma_settings,
                    'hash': hash,
                })
                open(os.path.join(grandma_dir, file_name % hash), 'w').write(data)
            subprocess.Popen('python manage_%s.py syncdb --noinput' % hash).wait()
            return render_to_response('grandma/restart.html', {
                'hash': hash,
            }, context_instance=RequestContext(request))
    else:
        form = GrandmaApplicationsForm()
    return render_to_response('grandma/apps.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def restart(request, hash):
    open('manage.py', 'w').write(open('manage_%s.py' % hash).read())
    return HttpResponse()

def started(requst):
    return HttpResponse()

def custom(request):
    return HttpResponse(content='YES')

def build(request):
    return HttpResponse()

def done(request):
    return HttpResponse()
