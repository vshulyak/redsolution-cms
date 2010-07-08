from django import forms
from grandma.models import GrandmaSettings

class GrandmaApplicationsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GrandmaApplicationsForm, self).__init__(*args, **kwargs)

        grandma_settings = GrandmaSettings.objects.get_settings()
        for application in grandma_settings.applications.all():
            self.fields['application_%d' % application.id] = forms.BooleanField(
                required=False, label=application.name, initial=application.install,
                help_text=application.description)

    def save(self):
        grandma_settings = GrandmaSettings.objects.get_settings()
        for application in grandma_settings.applications.all():
            application.install = self.cleaned_data['application_%d' % application.id]
            application.save()
