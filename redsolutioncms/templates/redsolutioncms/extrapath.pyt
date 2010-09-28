import sys
sys.path.extend([{% for package in cms_settings.packages.installed %}
    r'{{ package.path }}', {% endfor %}
])
