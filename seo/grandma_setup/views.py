from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import SettingsForm
from models import Settings

def index(self, request):
    settings = Settings()
    if request.method == 'POST':
        form = SettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            settings.seo_for_models = form.cleaned_data['seo_for_models']
            settings.save()
    else:
        form = SettingsForm(initial={
            'seo_for_models': settings.seo_for_models,
        })
    return render_to_response('seo/grandma/index.html', {
        'form': form,
    }, context_instance=RequestContext(request))
