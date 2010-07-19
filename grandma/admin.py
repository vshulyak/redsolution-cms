from django.contrib import admin
from django.contrib.admin import helpers
from django import forms, template
from django.forms.formsets import all_valid
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, ugettext_lazy
from django.utils.encoding import force_unicode

from grandma.models import GrandmaSettings, GrandmaPackage, GrandmaEntryPoint

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


HORIZONTAL, VERTICAL = 1, 2
# returns the <ul> class for a given radio_admin field
get_ul_class = lambda x: 'radiolist%s' % ((x == HORIZONTAL) and ' inline' or '')


class GrandmaBaseAdmin(admin.ModelAdmin):

    def __init__(self):
        self.opts = self.model._meta
        self.admin_site = None
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        if 'action_checkbox' not in self.list_display and self.actions is not None:
            self.list_display = ['action_checkbox'] + list(self.list_display)
        if not self.list_display_links:
            for name in self.list_display:
                if name != 'action_checkbox':
                    self.list_display_links = [name]
                    break
        super(GrandmaBaseAdmin, self).__init__(self.model, self.admin_site)

    # Redefine urls for views
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^(.+)/$', self.change_view, name='%s_%s_change' % info),
        )
        return urlpatterns

    def change_view(self, request):
        "The 'change' admin view for this model"
        model = self.model
        opts = model._meta

        try:
            obj = self.model.objects.get_settings()
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)

            from django.forms.formsets import all_valid

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet in self.get_formsets(request, obj):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        })
        context_instance = template.RequestContext(request)
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, context_instance=context_instance)
