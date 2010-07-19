from django.contrib import admin
from grandma.models import GrandmaSettings, GrandmaPackage, GrandmaEntryPoint, GrandmaCreatedModel

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

try:
    admin.site.register(GrandmaCreatedModel)
except admin.sites.AlreadyRegistered:
    pass
