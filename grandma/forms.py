from django import forms
from grandma.models import GrandmaSettings

class GrandmaPackagesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GrandmaPackagesForm, self).__init__(*args, **kwargs)

        grandma_settings = GrandmaSettings.objects.get_settings()
        for package in grandma_settings.packages.all():
            self.fields['package_%d' % package.id] = forms.BooleanField(
                required=False, label=package.verbose_name, initial=package.selected,
                help_text=package.description)

    def save(self):
        grandma_settings = GrandmaSettings.objects.get_settings()
        for package in grandma_settings.packages.all():
            package.selected = self.cleaned_data['package_%d' % package.id]
            package.save()
