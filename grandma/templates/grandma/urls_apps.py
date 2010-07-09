# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

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
    url(r'^$', 'grandma.views.index', name='index'),
    url(r'^apps$', 'grandma.views.apps', name='apps'),
    url(r'^restart/(?P<hash>\w{8})$', 'grandma.views.restart', name='restart'),
    url(r'^started$', 'grandma.views.started', name='started'),
    url(r'^custom$', 'grandma.views.custom', name='custom'),
    url(r'^build$', 'grandma.views.build', name='build'),
    url(r'^done$', 'grandma.views.done', name='done'),{% for module in modules %}
    (r'^custom/{{ module }}$', include('{{ module }}.grandma_setup.urls')),{% endfor %}
)
