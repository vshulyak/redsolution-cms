# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url, handler404, handler500
from django.conf import settings

handler404
handler500

urlpatterns = patterns('')

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += patterns('',
        (r'^admin/', include(admin.site.urls)),
    )
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns(
    '',
    url(r'^$', 'redsolutioncms.views.index', name='index'),
    url(r'^apps$', 'redsolutioncms.views.apps', name='apps'),
    url(r'^load$', 'redsolutioncms.views.load', name='load'),
    url(r'^restart$', 'redsolutioncms.views.restart', name='restart'),
    url(r'^started/$', 'redsolutioncms.views.started', name='started'),
    url(r'^custom$', 'redsolutioncms.views.custom', name='custom'),
    url(r'^build$', 'redsolutioncms.views.build', name='build'),
    url(r'^done$', 'redsolutioncms.views.done', name='done'),
    url(r'^cancel_lock/$', 'redsolutioncms.views.cancel_lock', name='cancel_lock'),
    url(r'^create_superuser/$', 'redsolutioncms.views.create_superuser', name='create_superuser'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog',
        {'packages': ('django.conf',)}, name='admin_jsi18n'),
)

try:
    from urls_additional import *
except ImportError:
    print 'Can not import urls_additional!'
