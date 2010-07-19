# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, handler404, handler500
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap

handler404
handler500

admin.autodiscover()
urlpatterns = patterns('')

sitemaps = {
}

if settings.DEBUG:
    pass

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^robots.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

#pages_dict = {
#    'queryset': Page.objects.exclude(status=Page.DRAFT),
#    'date_field': 'last_modification_date',
#}
#    'pages': GenericSitemap(pages_dict),
