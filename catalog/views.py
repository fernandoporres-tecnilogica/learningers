# -*- coding: utf-8 -*-
from catalog import forms, serializers
from catalog.models import available_resource_models, SessionWay, Resource, Way
from django.views.generic.base import View
from django.views import generic
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics
import reversion
from itertools import chain, imap, groupby
from operator import itemgetter
import rest_framework
from django.template.loader import render_to_string
from schedule.utils import coerce_date_dict
import datetime
from django.utils import timezone
from commons.versions import previous_version_instance

def initialize_search_form(geget):
    ret = forms.ResourceSearchForm()
    for key in ret.fields:
        if key in geget:
            ret.fields[key].initial = geget[key]
    return ret

class CatalogView(generic.ListView):
    """
    Listing des resources du catalogue.
    
    Utilisé surtout pour le développement.
    Peut-être à conserver par la suite pour lister les derniers ajouts.
    """
    model = Resource
    def get_context_data(self, **kwargs):
        context = {}
        context['search_form'] = initialize_search_form(self.request.GET)
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
        context['search_form'] = initialize_search_form(self.request.GET)
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
            if 'version' in self.request.GET:
                version = reversion.models.Version.objects.get(pk=self.request.GET['version'])
                obj = previous_version_instance(self.model,version.field_dict)
                return obj
            else:
                obj = get_object_or_404(self.model,slug=self.kwargs['slug'],**self.make_parents_query(self.kwargs))
                return obj
      
def make_resource_view(_resource_type):
    """
    Construit dynamiquement une vue spécifique à un type de resource, en dérivant de la vue générique ci-dessus.
    """      
    class HOP(BaseResourceView):
        model = available_resource_models[_resource_type]
        url = 'catalog:' + _resource_type
        template_name = 'catalog/' + _resource_type + '/view.html'
        resource_type = _resource_type
    return HOP.as_view()
    
class CreateResourceView(generic.TemplateView):
    """
    Page de création d'une nouvelle ressource, sélection du type de ressource à créer.
    
    Charge les types de ressources disponibles à partir de available_resource_models.
    """
    template_name= 'catalog/create_resource.html'
    def get_context_data(self, **kwargs):
        context = super(CreateResourceView, self).get_context_data(**kwargs)
        context['search_form'] = initialize_search_form(self.request.GET)
        context['resource_types'] = [ { 'name': resource_type, 'user_friendly_name': model._meta.verbose_name.title(), 'help_text': model.__doc__ } for resource_type,model in available_resource_models.items() ]
        if 'parent' in self.request.GET:
            context['parent'] = self.request.GET['parent']
        return context

def make_create_resource_view(resource_type):
    """
    Construit dynamiquement la page de formulaire de création d'une nouvelle resource en fonction du type de ressource.
    """
    class HOP(generic.CreateView):
        form_class = forms.make_resource_form(resource_type)
        template_name= 'catalog/create.html'
        model = available_resource_models[resource_type]
        def get_context_data(self, **kwargs):
            context = generic.CreateView.get_context_data(self, **kwargs)
            context['user_friendly_type'] = self.model._meta.verbose_name.title()
            return context
        def get_initial(self):
            initial = super(generic.CreateView, self).get_initial()
            if 'parent' in self.request.GET:
                initial['parent'] = Way.objects.get(pk=self.request.GET['parent'])
            else:
                initial['parent'] = SessionWay.objects.get(user=self.request.user)
            return initial
    return HOP.as_view()

class SearchResultsView(generic.TemplateView):
    """
    Affichage des résultats d'une recherche
    """
    template_name = 'catalog/search/results.html'
    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        # pass the search form to keep its contents
        form =  forms.ResourceSearchForm(self.request.GET)
        context['search_form'] = form
        return context

from rest_framework.response import Response
    
class RequestMoreSearchResults(rest_framework.views.APIView):
    """
    Affichage des résultats d'une recherche
    """
    serializer_class = serializers.ResourceSerializer
    def get(self,request,*args,**kwargs):
        # pass the search form to keep its contents
        val = forms.ResourceSearchForm(self.request.GET).search().values('rendered')
        return Response(val)

class CalendarRenderView(rest_framework.views.APIView):
    """
    Retourne le rendu HTML d'un calendrier
    """
    def get(self,request,*args,**kwargs):
        way = Way.objects.get(pk=kwargs['pk'])
        try:
            date = coerce_date_dict(request.GET)
        except ValueError:
            raise Http404  
        if date:
            try:
                date = datetime.datetime(**date)
            except ValueError:
                raise Http404
        else:
            date = timezone.now()
        period = way.get_month(date)
        args = { 'calendar':way.calendar, 'period':period, 'size':kwargs['size']  }
        prev_date = period.prev().start
        next_date = period.next().start
        val = {'rendered':render_to_string('schedule/calendar_month_compact.html',args),
               'prev_date': { 'year':prev_date.year, 'month':prev_date.month, 'day':prev_date.day, 'hour':prev_date.hour, 'minute':prev_date.minute,'second':prev_date.second },
               'next_date': { 'year':next_date.year, 'month':next_date.month, 'day':next_date.day, 'hour':next_date.hour, 'minute':next_date.minute,'second':next_date.second }
               }
        return Response(val)        
        
