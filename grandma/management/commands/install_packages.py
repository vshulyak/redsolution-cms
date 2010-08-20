# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from grandma.models import GrandmaSettings, GrandmaCreatedModel, \
    GrandmaEntryPoint
import os
from grandma.packages import install
from grandma.importpath import importpath

def uninstall_packages():
    '''
    Removes all records in all tables, from all modules.
    Set installed to False in all records in GrandmaPackages
    '''
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

def load_packages():
    """
    Downloads packages to eggs and imports them to sys.path
    TODO: Raise download error if download failed
    """
    grandma_settings = GrandmaSettings.objects.get_settings()
    # delete all old entry points, because we reset all settings at step 2
    GrandmaEntryPoint.objects.all().delete()
    selected_packages = grandma_settings.packages.filter(selected=True)
    # prepare modules...
    modules_to_download = [{'name': package.package, 'version': package.version, }
        for package in selected_packages]
    workset = install(modules_to_download,
        os.path.join(os.path.dirname(grandma_settings.grandma_dir), 'eggs'))
    # Now fetch entry points and import modules
    for package in selected_packages:
        distr = workset.by_key[package.package]
        distr.activate()

        package.path = distr.location
        entry_points = distr.get_entry_info(None, 'grandma_setup')

        installed = True
        if entry_points:
            for _, entry_point in entry_points.iteritems():
                try:
                    importpath(entry_point.module_name)
                except ImportError:
                    installed = False
                    break
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

        package.installed = installed
        package.save()

class Command(BaseCommand):

    def handle(self, *args, **options):
        import time
        time.sleep(10)
        uninstall_packages()
        load_packages()
