# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from redsolutioncms.models import CMSSettings, CMSCreatedModel, \
    CMSEntryPoint
import os
from redsolutioncms.packages import install
from redsolutioncms.importpath import importpath
from redsolutioncms.loader import home_dir

def uninstall_packages():
    '''
    Removes all records in all tables, from all modules.
    Set installed to False in all records in CMSPackages
    '''
    cms_settings = CMSSettings.objects.get_settings()
    if not cms_settings.packages.filter(selected=False, installed=True).count() and \
        not cms_settings.packages.filter(selected=True, installed=False).count():
        return
    for model in CMSCreatedModel.objects.all():
        try:
            importpath(model.name).objects.all().delete()
        except:
            pass
    for package in cms_settings.packages.installed():
        package.installed = False
        package.save()

def load_packages():
    """
    Downloads packages to eggs and imports them to sys.path
    TODO: Raise download error if download failed
    """
    cms_settings = CMSSettings.objects.get_settings()
    # delete all old entry points, because we reset all settings at step 2
    CMSEntryPoint.objects.all().delete()
    selected_packages = cms_settings.packages.filter(selected=True)
    # prepare modules...
    modules_to_download = [{'name': package.package, 'version': package.version, }
        for package in selected_packages]
    workset = install(modules_to_download, os.path.join(home_dir, 'eggs'))
    # Now fetch entry points and import modules
    for package in selected_packages:
        distr = workset.by_key[package.package]
        distr.activate()

        package.path = distr.location
        entry_points = distr.get_entry_info(None, 'redsolutioncms')

        installed = True
        if entry_points:
            for _, entry_point in entry_points.iteritems():
                try:
                    importpath(entry_point.module_name)
                except ImportError:
                    installed = False
                    break
                # Interactive setup feature
                try:
                    importpath(entry_point.module_name + '.urls')
                except ImportError:
                    has_urls = False
                else:
                    has_urls = True
                # Frontpage handler feature
                try:
                    importpath(entry_point.module_name + '.frontpage_handler')
                except ImportError:
                    frontpage_handler = False
                else:
                    frontpage_handler = True

                CMSEntryPoint.objects.create(
                    package=package,
                    module=entry_point.module_name,
                    has_urls=has_urls,
                    frontpage_handler=frontpage_handler)

        package.installed = installed
        package.save()

class Command(BaseCommand):

    def handle(self, *args, **options):
        import time
        time.sleep(10)
        uninstall_packages()
        load_packages()
