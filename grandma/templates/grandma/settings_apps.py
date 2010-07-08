from settings import *

INSTALLED_APPS += [{% for application in grandma_settings.applications.all %}{% if application.path %}{% for setup in application.setups.all %}
    '{{ setup.module }}',{% endfor %}{% endif %}{% endfor %}
]

ROOT_URLCONF = 'grandma.urls_apps'

