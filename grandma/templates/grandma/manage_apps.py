#!/usr/bin/env python
import os
import sys
sys.path.extend([{ % for path in paths % }
    '{{ path }}', { % endfor % }
])
sys.path[0:0] = [
    os.path.abspath('.'),
    os.path.abspath(__file__),
    os.path.abspath(os.path.join('..', 'parts', 'django'))
]

from django.core.management import execute_manager
try:
    import settings_apps # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings_apps)
