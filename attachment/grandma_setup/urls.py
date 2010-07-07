# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'attachment.grandma_setup.views.index', name='attachment_index'),
)
