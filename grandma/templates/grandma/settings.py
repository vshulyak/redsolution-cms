from settings import *

INSTALLED_APPS += [{% for package in grandma_settings.packages.all %}{% if package.ok %}{% for entry_point in package.entry_points.all %}
    '{{ entry_point.module }}', {% endfor %}{% endif %}{% endfor %}
]

ROOT_URLCONF = 'grandma.urls_{{ hash }}'

CURRENT_HASH = '{{ hash }}'
{% if prev_hash %}PREV_HASH = '{{ prev_hash }}'
{% endif %}