# -*- coding: utf-8 -*-

import os

gettext_noop = lambda s: s

ADMINS = (
#    ('src', 'src@redsolution.ru'),
)

MANAGERS = (
#    ('manager', 'manager@redsolution.ru'),
)

EMAIL_SUBJECT_PREFIX = '[{{ cms_settings.project_name }}]'

DATABASE_ENGINE = '{{ cms_settings.database_engine }}'
DATABASE_NAME = '{{ cms_settings.database_name }}'
DATABASE_USER = '{{ cms_settings.database_user }}'
DATABASE_PASSWORD = '{{ cms_settings.database_password }}'
DATABASE_HOST = '{{ cms_settings.database_host }}'
DATABASE_PORT = '{{ cms_settings.database_port }}'

TIME_ZONE = 'Asia/Yekaterinburg' # Fix me

LANGUAGE_CODE = 'ru' # Fix me

SITE_ID = 1

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
UPLOAD_DIR = 'upload'

MEDIA_URL = '/media/'
UPLOAD_URL = os.path.join(MEDIA_URL, UPLOAD_DIR)

ADMIN_MEDIA_PREFIX = '/admin_media/'

SECRET_KEY = 'i*1gdd^(gvx70fb0d5*6!q7^a7r^)=mf)ip+i07%v*lj+=ir@l' # Fix me

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
]

ROOT_URLCONF = '{{ cms_settings.project_name }}.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
]

TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
]

FIXTURE_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures'),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
]

# Server settings
FORCE_SCRIPT_NAME = ''

CACHE_BACKEND = 'locmem:///?max_entries=5000'
