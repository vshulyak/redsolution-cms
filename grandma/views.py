import os
import random
import subprocess
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from grandma.importpath import importpath
from grandma.models import GrandmaSettings, GrandmaEntryPoint, \
    GrandmaCreatedModel
from grandma.forms import GrandmaPackagesForm, UserCreationForm
from grandma.packages import search_index, install
from grandma.make import AlreadyMadeException
import pexpect

CONFIG_FILES = ['manage', 'settings', 'urls', ]

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
    workset = install(modules_to_download, os.path.join(grandma_settings.project_dir, 'eggs'))
    # Now fetch entry points and import modules
    for package in selected_packages:
        distr = workset.by_key[package.package]
        distr.activate()

        package.path = distr.location
        package.installed = True
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
    if not grandma_settings.packages.filter(selected=False, installed=True).count() and \
        not grandma_settings.packages.filter(selected=True, installed=False).count():
        return
    for model in GrandmaCreatedModel.objects.all():
        try:
            importpath(model.name).objects.all().delete()
        except:
            pass
    for package in grandma_settings.packages.installed():
        package.installed = False
        package.save()

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
    uninstall_packages()
    load_packages()
    grandma_settings = GrandmaSettings.objects.get_settings()
    hash = '%08x' % random.randint(0, 0x100000000)
    prev_hash = getattr(settings, 'CURRENT_HASH', None)
    for file_name in CONFIG_FILES:
        data = render_to_string('grandma/%s.py' % (file_name), {
            'grandma_settings': grandma_settings,
            'hash': hash,
            'prev_hash': prev_hash,
        })
        open(os.path.join(grandma_settings.grandma_dir, '%s_%s.py' % (file_name, hash)), 'w').write(data)
    manage_name = os.path.join(grandma_settings.grandma_dir, 'manage_%s.py' % hash)
    subprocess.Popen('python %s syncdb --noinput' % manage_name, shell=os.sys.platform != 'win32').wait()
    return render_to_response('grandma/load.html', {
        'hash': hash,
    }, context_instance=RequestContext(request))

def restart(request, hash):
    """
    User can`t see it. It will be called by javascript.
    Rewrite manage.py for current server, so server will be restarted.
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    source = os.path.join(grandma_settings.grandma_dir, 'manage_%s.py' % hash)
    destination = os.path.join(grandma_settings.grandma_dir, 'manage.py')
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
    try:
        prev_hash = settings.PREV_HASH
        for file_name in ['manage', 'settings', 'urls', ]:
            for extention in ['py', 'pyc']:
                try:
                    os.remove(os.path.join(grandma_settings.grandma_dir, '%s_%s.%s' % (file_name, prev_hash, extention)))
                except OSError:
                    pass
    except AttributeError:
        pass
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

def build(request):
    grandma_settings = GrandmaSettings.objects.get_settings()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            bootstrap_name = os.path.join(grandma_settings.grandma_dir, '..', 'bootstrap.py')
            subprocess.Popen('python %s' % bootstrap_name, shell=os.sys.platform != 'win32').wait()
            buildout_name = os.path.join(grandma_settings.grandma_dir, '..', 'bin', 'buildout')
            subprocess.Popen('python %s -c develop.cfg' % buildout_name, shell=os.sys.platform != 'win32').wait()
            django_name = os.path.join(grandma_settings.grandma_dir, '..', 'bin', 'django')
            subprocess.Popen('python %s syncdb --noinput' % django_name, shell=os.sys.platform != 'win32').wait()
#            create superuser
            child = pexpect.spawn('python %s createsuperuser' % django_name)
            child.expect("Username.*")
            child.sendline(form.cleaned_data['username'])
            child.expect("E-mail.*")
            child.sendline(form.cleaned_data['email'])
            child.expect("Password.*")
            child.sendline(form.cleaned_data['password1'])
            child.expect("Password.*")
            child.sendline(form.cleaned_data['password1'])
            child.expect("Superuser.*")

#            TODO: here we want to execute new server. But view will not return until subprocess will die.
#            Maybe we need to start execution in separate view by AJAX.
#            Or maybe we need to replace manage.py.
#            subprocess.Popen('python %s runserver 127.0.0.1:8001' % django_name, shell=os.sys.platform != 'win32')
            return HttpResponseRedirect(reverse('done'))
    else:
        form = UserCreationForm()
    return render_to_response('grandma/build.html', {
        'grandma_settings': grandma_settings,
        'bootstart': os.path.join(grandma_settings.project_dir, 'bootstrap.py'),
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
