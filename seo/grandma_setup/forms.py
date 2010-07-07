# -*- coding: utf-8 -*-

from django import forms

class SettingsForm(forms.Form):
    seo_for_models = forms.CharField(label=u'Model')
