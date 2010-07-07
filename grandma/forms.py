from django.forms.models import ModelForm
from grandma.models import GrandmaSettings

class GrandmaSettingsForm(ModelForm):
    class Meta:
        model = GrandmaSettings
