from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from grandma.models import get_last_settings, GrandmaSettings
from grandma.forms import GrandmaSettingsForm

def index(request):
    settings = get_last_settings(GrandmaSettings)
    if request.method == 'POST':
        form = GrandmaSettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = GrandmaSettingsForm(instance=settings)
    return render_to_response('grandma/index.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def apps(request):
    settings = get_last_settings(GrandmaSettings)
    if request.method == 'POST':
        form = GrandmaSettingsForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('apps'))
    else:
        form = GrandmaSettingsForm(instance=settings)
    return render_to_response('grandma/apps.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def custom(request):
    return HttpResponse()

def build(request):
    return HttpResponse()

def done(request):
    return HttpResponse()
