from django.contrib import admin
from grandma.models import GrandmaSettings, GrandmaApplication, GrandmaSetup

class GrandmaSetupInline(admin.TabularInline):
    model = GrandmaSetup

class GrandmaApplicationForm(admin.ModelAdmin):
    model = GrandmaApplication
    inlines = [GrandmaSetupInline]

try:
    admin.site.register(GrandmaSettings)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(GrandmaApplication, GrandmaApplicationForm)
except admin.sites.AlreadyRegistered:
    pass
