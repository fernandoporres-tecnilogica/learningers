# -*- coding: utf-8 -*-
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
from curses.ascii import ascii

class CatalogView(generic.ListView):
    """
    Listing des resources du catalogue.
    
    Utilisé surtout pour le développement.
    Peut-être à conserver par la suite pour lister les derniers ajouts.
    """
    model = Resource
    def get_context_data(self, **kwargs):
        context = {}
        context['search_form'] = forms.ResourceSearchForm(self.request.GET)
        context['resources'] = Resource.objects.select_subclasses()
        return context
    

class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Accès AJAX aux données d'une resource.
    
    Utilisé surtout pour effacer des resources.
    """
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
                        
class BaseResourceView(View,generic.base.TemplateResponseMixin):
    """
    Vue de base pour toutes les resources.
    """
    @staticmethod
    def make_parents_query(kwargs):
        """
        Construit les arguments de la requête SQL pour accéder à une resource
        en utilisant le chemin d'accès fourni par l'URL dispatcher.  
        """
        ret = {}
        parent_field = 'parent'
        print kwargs
        for j in range(0,4):
            parent_slug = ('slug%d' % j)
            if parent_slug in kwargs:
                ret.update({parent_field + '__slug': kwargs[parent_slug]})
                parent_field += '__parent'
            else:
                break
        print ret
        return ret
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
            obj = get_object_or_404(self.model,slug=self.kwargs['slug'],**self.make_parents_query(self.kwargs))
            return obj
      
def make_resource_view(_resource_type):
    """
    Construit dynamiquement une vue spécifique à un type de resource, en dérivant de la vue générique ci-dessus.
    """      
    class HOP(BaseResourceView):
        model = available_resource_models[_resource_type]
        url = 'catalog:' + _resource_type
        template_name = 'catalog/view/' + available_resource_models[_resource_type].data_type + '.html'
        resource_type = _resource_type
    return HOP.as_view()
    
class CreateResourceView(generic.TemplateView):
    """
    Page de création d'une nouvelle ressource, sélection du type de ressource à créer.
    
    Charge les types de ressources disponibles à partir de available_resource_models.
    """
    template_name= 'catalog/create/resource.html'
    def get_context_data(self, **kwargs):
        context = super(CreateResourceView, self).get_context_data(**kwargs)
        context['search_form'] = forms.ResourceSearchForm(self.request.GET)
        context['resource_types'] = [ { 'name': model.resource_type, 'user_friendly_name': model.user_friendly_type, 'help_text': model.__doc__ } for model in available_resource_models.values() ]
        return context

def make_create_resource_view(resource_type):
    """
    Construit dynamiquement la page de formulaire de création d'une nouvelle resource en fonction du type de ressource.
    """
    class HOP(generic.CreateView):
        form_class = forms.make_resource_form(resource_type)
        template_name= 'catalog/create/' + resource_type + '.html'
        model = available_resource_models[resource_type]
        def get_form(self, form_class):
            print form_class
            toto = generic.CreateView.get_form(self, form_class)
            print "boing"
            print (toto.as_ul())
            return toto
        def get_context_data(self, **kwargs):
            context = generic.CreateView.get_context_data(self, **kwargs)
            context['user_friendly_type'] = self.model.user_friendly_type
            return context
        def get_initial(self):
            initial = super(generic.CreateView, self).get_initial()
            initial['parent'] = SessionWay.objects.get(user=self.request.user)
            return initial
    return HOP.as_view()
