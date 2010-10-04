# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, handler404, handler500, url
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap

handler404
handler500

admin.autodiscover()
urlpatterns = patterns('')

sitemaps = {}

if settings.DEBUG:
    pass

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

#------------------------------------------------------------------------------
#                       Custom applicaitons urls
#------------------------------------------------------------------------------
