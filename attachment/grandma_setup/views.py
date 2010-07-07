from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory, modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from grandma.models import get_last_settings
from models import AttachmentSettings, AttachmentForModels, AttachmentLinkModels

def index(request):
    settings = get_last_settings(AttachmentSettings)
    form_class = modelform_factory(AttachmentSettings)
    for_formset_class = inlineformset_factory(AttachmentSettings, AttachmentForModels)
    link_formset_class = inlineformset_factory(AttachmentSettings, AttachmentLinkModels)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            settings = form.save(commit=False)
            for_formset = for_formset_class(request.POST, request.FILES, instance=settings)
            link_formset = link_formset_class(request.POST, request.FILES, instance=settings)
            if for_formset.is_valid() and link_formset.is_valid():
                settings.save()
                for_formset.save()
                link_formset.save()
                return HttpResponseRedirect(reverse('custom'))
        else:
            for_formset = for_formset_class(request.POST, request.FILES, instance=settings)
            link_formset = link_formset_class(request.POST, request.FILES, instance=settings)
    else:
        form = form_class(instance=settings)
        for_formset = for_formset_class(instance=settings)
        link_formset = link_formset_class(instance=settings)
    return render_to_response('attachment/grandma/index.html', {
        'form': form,
        'for_models_formset': for_formset,
        'link_formset': link_formset,
    }, context_instance=RequestContext(request))
