# -*- coding: utf-8 -*-
from urls import *

urlpatterns += patterns('',{% for package in cms_settings.packages.installed %}{% for entry_point in package.entry_points.has_urls %}
    (r'^custom/{{ entry_point.module }}$', include('{{ entry_point.module }}.urls')),{% endfor %}{% endfor %}
)
