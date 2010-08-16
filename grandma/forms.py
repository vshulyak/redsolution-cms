from django import forms
from django.utils.translation import ugettext_lazy as _
from grandma.models import GrandmaSettings

class GrandmaPackagesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GrandmaPackagesForm, self).__init__(*args, **kwargs)

        cms_settings = GrandmaSettings.objects.get_settings()
        for package in cms_settings.packages.all():
            self.fields['package_%d' % package.id] = forms.BooleanField(
                required=False, label=package.verbose_name, initial=package.selected,
                help_text=package.description)

    def save(self):
        cms_settings = GrandmaSettings.objects.get_settings()
        for package in cms_settings.packages.all():
            package.selected = self.cleaned_data['package_%d' % package.id]
            package.save()

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
