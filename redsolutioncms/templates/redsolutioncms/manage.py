#!/usr/bin/env python
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([{% for package in cms_settings.packages.installed %}
    r'{{ package.path }}', { % endfor % }
])
