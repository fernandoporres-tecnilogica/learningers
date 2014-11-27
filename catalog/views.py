from catalog import forms, serializers
from catalog.models import available_resource_models, SessionWay, Resource
from django.views.generic.base import View
from django.views import generic
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics
import reversion

class CatalogView(generic.ListView):
    model = Resource
    def get_context_data(self, **kwargs):
        context = {}
        context['search_form'] = forms.ResourceSearchForm(self.request.GET)
        context['resources'] = Resource.objects.select_subclasses()
        return context
    

class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
 
def make_parents_query(kwargs):
    ret = {}
    parent_field = 'parent'
    for j in range(0,4):
        parent_slug = ('slug%d' % j)
        if parent_slug in kwargs:
            ret.update({parent_field + '__slug': kwargs[parent_slug]})
            parent_field += '__parent'
        else:
            break
    return ret
                        
# Create your views here.
class BaseResourceView(View,generic.base.TemplateResponseMixin):
    def get_context_data(self, **kwargs):
        context = {}
        context['search_form'] = forms.ResourceSearchForm(self.request.GET)
        context['resource'] = kwargs['object']
        # Build a list of all previous versions, latest versions first, duplicates removed:
        context['versions'] = reversion.get_for_object(kwargs['object'])          
        return context
    
    def get(self, request, **kwargs):
        self.object = self.get_object()
        obj_url = self.object.get_absolute_url()
        if request.path != obj_url:
            return HttpResponsePermanentRedirect(obj_url)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def get_object(self):
        if not 'slug0' in self.kwargs and self.resource_type is not 'way':
            qs = self.model.objects.filter(
                 parent=self.request.way,
                 slug=self.kwargs['slug']
            )            
            if(qs.count() == 0):
                obj = self.model.make_from_slug(self.request.way,self.kwargs['slug'])
                try:
                    obj.full_clean()
                except ValidationError as e:
                    raise Http404(e)
                obj.save()
                return obj
            else:
                return qs.get()
        else:
            if not 'slug' in self.kwargs:
                return self.request.way
            if 'rev' in self.request.GET:
                version = reversion.models.Version.objects.get(pk=self.request.GET['rev'])
                version.revision.revert()
            obj = get_object_or_404(self.model,slug=self.kwargs['slug'],**make_parents_query(self.kwargs))
            return obj
      
def make_resource_view(_resource_type):      
    class HOP(BaseResourceView):
        model = available_resource_models[_resource_type]
        url = 'catalog:' + _resource_type
        template_name = 'catalog/view/' + available_resource_models[_resource_type].data_type + '.html'
        resource_type = _resource_type
    return HOP.as_view()
    
class CreateResourceView(generic.TemplateView):
    template_name= 'catalog/create/choice.html'
    def get_context_data(self, **kwargs):
        context = super(CreateResourceView, self).get_context_data(**kwargs)
        context['search_form'] = forms.EntriesSearchForm(self.request.GET)
        context['entry_types'] = [ { 'name': model.entry_type, 'user_friendly_name': model.user_friendly_type, 'help_text': model.help_text } for model in models.available_entry_models.values() ]
        return context

def make_create_resource_view(entry_type):
    class HOP(generic.CreateView):
        form_class = forms.make_entry_form(entry_type)
        template_name= 'catalog/create/' + entry_type + '.html'
        model = available_entry_models[entry_type]
    def get_initial(self):
        initial = super(CreateEntryView, self).get_initial()
        initial['parent'] = models.UserParcours.objects.get(user=self.request.user)
        return initial
    return HOP.as_view()
