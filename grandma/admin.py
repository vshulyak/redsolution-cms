from django.contrib import admin
from grandma.models import GrandmaSettings, GrandmaPackage, GrandmaEntryPoint

try:
    admin.site.register(GrandmaSettings)
except admin.sites.AlreadyRegistered:
    pass

class GrandmaEntryPointInline(admin.TabularInline):
    model = GrandmaEntryPoint

class GrandmaPackageForm(admin.ModelAdmin):
    model = GrandmaPackage
    inlines = [GrandmaEntryPointInline]

try:
    admin.site.register(GrandmaPackage, GrandmaPackageForm)
except admin.sites.AlreadyRegistered:
    pass
