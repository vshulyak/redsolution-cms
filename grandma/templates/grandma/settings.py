from settings import *

DATABASE_NAME = 'grandma_{{ hash }}.sqlite'

INSTALLED_APPS += [{% for package in grandma_settings.packages.all %}{% if package.ok %}{% for entry_point in package.entry_points.all %}
    '{{ entry_point.module }}', {% endfor %}{% endif %}{% endfor %}
]

ROOT_URLCONF = 'grandma.urls_{{ hash }}'
