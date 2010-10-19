from django import forms
from django.utils.translation import ugettext_lazy as _
from redsolutioncms.models import CMSSettings, CMSEntryPoint, Category

class FrontpageForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(FrontpageForm, self).__init__(*args, **kwargs)
        self.fields['frontpage'] = forms.ChoiceField(
            label=_('Choose frontpage handler'),
            choices=self.get_fronpage_handlers(),
        )

    def get_fronpage_handlers(self):
        installed_packages = CMSSettings.objects.get_settings().packages.installed()
        handlers = []
        for package in installed_packages:
            for entry_point in package.entry_points.frontpage_handlers():
                handlers.append((entry_point.module, package.verbose_name),)
        return handlers

    def save(self):
        '''Write frontpage setting to global CMS settings'''
        entry_point = CMSEntryPoint.objects.get(module=self.cleaned_data['frontpage'])
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.frontpage_handler = entry_point
        cms_settings.save()
    
class UserCreationForm(forms.Form):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message=_("This value must contain only letters, numbers and underscores."), initial='admin')
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    email = forms.EmailField(label=_("E-mail"), max_length=75, initial='admin@example.com')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
