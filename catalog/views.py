# -*- coding: utf-8 -*-
from catalog import forms, serializers
from catalog.models import available_resource_models, SessionWay, Resource, Way, available_search_engines, available_annotation_ranges, available_annotation_contents, Comment
from django.views.generic.base import View
from django.views import generic
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics
from django.utils.translation import ugettext as _
import reversion
from itertools import chain, imap, groupby
from operator import itemgetter
import rest_framework
from django.template.loader import render_to_string
from schedule.utils import coerce_date_dict
import datetime
from django.utils import timezone
from commons.versions import previous_version_instance
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import filters
from django.utils.text import slugify

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

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Accès AJAX aux données d'une resource.
    
    Utilisé surtout pour effacer des resources.
    """
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

class CommentCreateView(generics.ListCreateAPIView):
    """
    Accès AJAX aux données d'une resource.
    
    Utilisé surtout pour effacer des resources.
    """
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
                            
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
        context['comment_categories'] = ({'name':c[1], 'queryset':context['resource'].comments.filter(category=c[0])} for c in Comment.CATEGORY_CHOICES)            
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
        if not 'slug0' in self.kwargs and not 'way' in self.resource_type:
            qs = self.model.objects.filter(
                 parent=self.request.way,
                 slug=self.kwargs['slug']
            )            
            if(qs.count() == 0):
                try:
                    obj = self.model.make_from_slug(self.request.way,self.kwargs['slug'])
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
                qs = self.model.objects.filter(slug=self.kwargs['slug'],**self.make_parents_query(self.kwargs))
                if(qs.count() == 0):
                    try:
                        obj = self.model.make_from_slug(self.request.way,self.kwargs['slug'])
                        obj.full_clean()
                    except ValidationError as e:
                        raise Http404(e)
                    obj.save() 
                    return obj
                else:
                    return qs.get()
      
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
    
class PublishView(generic.RedirectView):
    permanent = False
    pattern_name = 'catalog:way-view'
    def get_redirect_url(self,*args,**kwargs):
        # extract way from sessionway
        toto = Way.objects.get(pk=self.request.way.way_ptr)
        # fix slug
        toto.slug = slugify(toto.name)
        if(_('Ajouter un titre...') in toto.name):
            raise ValidationError('Nom du parcours invalide!')
        kwargs['slug'] = toto.slug
        print "slug : %s" % toto.slug
        # validate it
        toto.full_clean()
        # recreate empty way 
        self.request.way.delete()
        # save it
        toto.save()
        user_parcours = SessionWay(user=self.request.user)
        user_parcours.save()
        self.request.session['way'] = user_parcours.pk
        url = super(PublishView, self).get_redirect_url(*args, **kwargs)
        print "url : %s" % url
        return url
   
class CopyView(generic.RedirectView):
    permanent = False
    def get_redirect_url(self,*args,**kwargs):
        resource = Resource.objects.get_subclass(pk=kwargs['pk'])
        resource.parent = self.request.way
        resource.pk = None
        resource.save()
        return resource.get_absolute_url() 
 
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
        context['available_search_engines'] = available_search_engines
        return context
    
class RequestMoreSearchResults(rest_framework.views.APIView):
    """
    Affichage des résultats d'une recherche
    """
    serializer_class = serializers.ResourceSerializer
    def get(self,request,*args,**kwargs):
        # pass the search form to keep its contents
        print "request"
        print self.request.GET
        f = forms.ResourceSearchForm(self.request.GET)
        if(f.is_valid()):
            print "data"
            print f.cleaned_data
            val = f.search().values('rendered')
            return Response(list(val))
        else:
            print "not valid!!"
            print f['t'].errors
            return Response([])

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
        

def make_annotation_viewset(content_type,range_type):
    """Generate a Viewset to load annotations via AJAX"""
    class AnnotationViewSet(viewsets.ModelViewSet):
        queryset = available_annotation_contents[content_type].objects.all()
        serializer_class = serializers.make_annotation_serializer(content_type,range_type)
        permission_classes = (permissions.AllowAny,)
        filter_backends = (filters.DjangoFilterBackend,)
        filter_fields = ('resource',)
    return AnnotationViewSet

import json
from django.http import HttpResponse

def make_externalsearch_view(SearchClass):
    """Generate view for obtaining external search results via AJAX"""
    class HOP(View,SearchClass):
        def get(self,request):
            querystring = self.request.GET['q']
            queryloc = self.request.GET['a']
            querylang = self.request.LANGUAGE_CODE
            search_results = list({ 'rendered': render_to_string('catalog/resource.html', result) } for result in self.search(querystring,queryloc,querylang))
            return HttpResponse(json.dumps(search_results, ensure_ascii=False), content_type='application/json; charset=UTF-8',)
    return HOP.as_view()
