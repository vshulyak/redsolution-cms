from settings import *

INSTALLED_APPS += [{ % for module in modules % }
    '{{ module}}', { % endfor % }
]

GRANDMA_APPS += [{ % for module in modules % }
    '{{ module}}', { % endfor % }
]
