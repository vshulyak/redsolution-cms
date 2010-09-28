from redsolutioncms.settings import *

INSTALLED_APPS += [{% for package in cms_settings.packages.installed %}{% for entry_point in package.entry_points.all %}
    '{{ entry_point.module }}',{% endfor %}{% endfor %}
]




{% comment %}
CURRENT_HASH = '{{ hash }}'
{% if prev_hash %}PREV_HASH = '{{ prev_hash }}'
{% endif %}
{% endcomment %}