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
from grandma.models import GrandmaSettings, GrandmaSetup
from grandma.forms import GrandmaApplicationsForm
from grandma.packages import search_index, install


def list_applications():
    """
    List applications.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    all_packages = search_index('grandma')

    if not grandma_settings.applications.count():
        for package in all_packages:
            grandma_settings.applications.create(
                selected=False,
                package=package['name'],
                version=package['version'],
                verbose_name=package['name'].replace('django-', '').replace('grandma.', ''),
                description=package['summary']
            )

def find_entry_points(package):
    """
    Find entry point in package for grandma_setup.
    """
    return [package.replace('django-', '') + '.grandma_setup']

def load_applications():
    """
    Downloads package to egg and imports it to sys.path
    TODO: Raise download error if download failed
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    GrandmaSetup.objects.all().delete()
    selected_packages = grandma_settings.applications.filter(selected=True)
    # prepare modules...
    modules_to_download = [{'name': package.package, 'version': package.version}
        for package in selected_packages]
    workset = install(modules_to_download)
    # Now fetch entry points and import modules
    for package in selected_packages:
        distr = workset.by_key[package.package]
        distr.activate()
        entry_points = distr.get_entry_info(None, 'grandma_setup')

        if entry_points:
            for ep_name, entry_point in entry_points.iteritems():
                try:
                    importpath(entry_point.module_name)
                except ImportError:
                    continue
                try:
                    importpath(entry_point.module_name + '.urls')
                except ImportError:
                    has_urls = False
                else:
                    has_urls = True
                GrandmaSetup.objects.create(
                    application=package, module=entry_point.module_name, has_urls=has_urls)

def index(request):
    """
    User can set base settings.
    Show base settings.
    Saves base settings.
    """
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
    """
    User can select applications.
    Fetches list of available applications. 
    Saves settings.
    """
    list_applications()
    if request.method == 'POST':
        form = GrandmaApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('load'))
    else:
        form = GrandmaApplicationsForm()
    return render_to_response('grandma/apps.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def load(request):
    """
    User can wait.
    Fetches applications. 
    Saves installation information for applications.
    Makes settings.py, urls.py, manage.py with installed setup-applications.
    Syncdb for setup-applications.
    """
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
    manage_name = os.path.join(grandma_dir, 'manage_%s.py' % hash)
    subprocess.Popen('python %s syncdb --noinput' % manage_name, shell=True).wait()
    return render_to_response('grandma/load.html', {
        'hash': hash,
    }, context_instance=RequestContext(request))

def restart(request, hash):
    """
    User can`t see it. It will be called by javascript.
    Rewrite manage.py for current server, so server will be restarted.
    """
    grandma_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(grandma_dir, 'manage_%s.py' % hash)
    destination = os.path.join(grandma_dir, 'manage.py')
    open(destination, 'w').write(open(source).read())
    return HttpResponse()

def started(requst):
    """
    User can`t see it. It will be called by javascript.
    Used to check, whether server is available after restart.
    """
    return HttpResponse()

def custom(request):
    """
    User can go to detail settings for applications or can ask to make project.
    Make files for new project.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        applications = ['grandma']
        for package in grandma_settings.applications.filter(ok=True):
            for entry_point in package.setups.all():
                applications.append(entry_point.module)
        make_objects = []
        for application in applications:
            try:
                make_class = importpath('.'.join([application, 'make', 'Make']))
            except ImportError:
                continue
            make_objects.append(make_class())
        try:
            os.mkdir(os.path.join(grandma_settings.project_path, grandma_settings.project_name))
        except OSError:
            pass
        for make_object in make_objects:
            make_object.premake()
        for make_object in make_objects:
            make_object.make()
        for make_object in make_objects:
            make_object.postmake()
        return HttpResponseRedirect(reverse('build'))
    return render_to_response('grandma/custom.html', {
        'grandma_settings': grandma_settings,
    }, context_instance=RequestContext(request))

def build(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    return render_to_response('grandma/build.html', {
        'grandma_settings': grandma_settings,
    }, context_instance=RequestContext(request))

def done(request):
    return HttpResponse()
