from settings import *

GRANDMA_APPS = [{ % for module in modules % }
    '{{ module }}', { % endfor % }
]

INSTALLED_APPS += GRANDMA_APPS

ROOT_URLCONF = 'grandma.urls_apps'

