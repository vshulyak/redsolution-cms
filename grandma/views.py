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
from grandma.models import GrandmaSettings, GrandmaEntryPoint
from grandma.forms import GrandmaPackagesForm
from grandma.packages import search_index, install
from grandma.make import AlreadyMadeException

def list_packages():
    """
    List packages.
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

def load_packages():
    """
    Downloads package to egg and imports it to sys.path
    TODO: Raise download error if download failed
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    GrandmaEntryPoint.objects.all().delete()
    selected_packages = grandma_settings.packages.filter(selected=True)
    # prepare modules...
    modules_to_download = [{'name': package.package, 'version': package.version, }
        for package in selected_packages]
    workset = install(modules_to_download)
    # Now fetch entry points and import modules
    for package in selected_packages:
        distr = workset.by_key[package.package]
        distr.activate()

        package.ok = True
        package.path = distr.location
        package.save()

        entry_points = distr.get_entry_info(None, 'grandma_setup')

        if entry_points:
            for _, entry_point in entry_points.iteritems():
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
                GrandmaEntryPoint.objects.create(
                    package=package,
                    module=entry_point.module_name,
                    has_urls=has_urls)

def uninstall_packages():
    grandma_settings = GrandmaSettings.objects.get_settings()
    for _ in grandma_settings.packages.filter(selected=False, ok=True):
        pass

def index(request):
    """
    User can set base settings.
    Shows base settings.
    Saves base settings.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    grandma_settings_class = modelform_factory(GrandmaSettings, exclude=['project_path'])
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
    uninstall_packages()
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
    uninstall_packages()
    load_packages()
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
    subprocess.Popen('python %s syncdb --noinput' % manage_name, shell=os.sys.platform != 'win32').wait()
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
    User can go to detail settings for packages or can ask to make project.
    Make files for new project.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        entry_points = ['grandma']
        for package in grandma_settings.packages.filter(ok=True):
            for entry_point in package.entry_points.all():
                entry_points.append(entry_point.module)
        make_objects = []
        for entry_point in entry_points:
            try:
                make_class = importpath('.'.join([entry_point, 'make', 'Make']))
            except ImportError:
                continue
            make_objects.append(make_class())
        try:
            os.mkdir(os.path.join(grandma_settings.project_path, grandma_settings.project_name))
        except OSError:
            pass
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

def build(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        grandma_dir = os.path.dirname(os.path.abspath(__file__))
        bootstrap_name = os.path.join(grandma_dir, '..', 'bootstrap.py')
        subprocess.Popen('python %s' % bootstrap_name, shell=os.sys.platform != 'win32').wait()
        buildout_name = os.path.join(grandma_dir, '..', 'bin', 'buildout')
        subprocess.Popen('python %s -c develop.cfg' % buildout_name, shell=os.sys.platform != 'win32').wait()
        return HttpResponseRedirect(reverse('done'))
    return render_to_response('grandma/build.html', {
        'grandma_settings': grandma_settings,
    }, context_instance=RequestContext(request))

def done(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    return render_to_response('grandma/done.html', {
        'grandma_settings': grandma_settings,
    }, context_instance=RequestContext(request))
