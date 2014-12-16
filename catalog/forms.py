# -*- coding: utf-8 -*-

from haystack.forms import SearchForm
from recurrence.forms import RecurrenceField
from django import forms
from ajax_select.fields import AutoCompleteField, AutoCompleteSelectField
from geopy import geocoders
from django.utils.translation import ugettext_lazy as __
from django_markdown.widgets import MarkdownWidget
from models import available_resource_models, GeoLocation
from formfield.fields import FormField
from django.utils import six
from django.forms.models import ModelFormMetaclass, BaseModelForm
from schedule.models import Event, Rule
from haystack.utils.geo import Point, D
import geopy

class ResourceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = True
        kwargs['label_suffix'] = ''
        super(ResourceSearchForm, self).__init__(*args, **kwargs)
    q = forms.CharField(label=__(u'Quoi?'), initial='',required=True)
    a = AutoCompleteField('location',help_text='',label=__(u'Où?'), initial='',required=False)
    t = RecurrenceField(label=__(u'Quand?'), initial='',required=False,max_rdates=0,max_exdates=0)
    
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(ResourceSearchForm, self).search()
        address = self.cleaned_data.get('a')
        if(address):
            g = geocoders.Nominatim() # this should be changed to openstreetmap
            try:
                place, (lat, lng) = g.geocode(address)
                print "address: %s, lat : %g, lng : %g" % (address, lat, lng)
                loc = Point(lng,lat)
                max_dist = D(km=10)
                #return sqs.dwithin('location',loc,max_dist).distance('location',loc)
            except geopy.exc.GeocoderServiceError:  
                pass
        return sqs
    def no_query_found(self):
        return self.searchqueryset.all()

class GeoLocationForm(forms.ModelForm):
    "Formulaire pour la localisation"
    class Meta:
        model = GeoLocation
        fields = '__all__'
       
def make_resource_form(resource_type):
    model_class = available_resource_models[resource_type]
    
    class BetterMetaClass(ModelFormMetaclass):
        def __new__(mcs, name, bases, attrs):
            new_attrs = {}
            new_attrs['description'] = forms.CharField(widget=MarkdownWidget()) 
            if(hasattr(model_class,'geo')):
                new_attrs['geo'] = FormField(GeoLocationForm)
            if(hasattr(model_class,'picture')):
                new_attrs['picture'] = FormField(ImageForm)  
            if(hasattr(model_class,'user')):
                new_attrs['user'] = AutoCompleteSelectField('user',required=False)  
            opts = model_class._meta
            # Avoid circular import
            from django.db.models.fields import Field as ModelField
            sortable_virtual_fields = [f for f in opts.virtual_fields
                                       if isinstance(f, ModelField)]
            fields = dict((f.name, f) for f in sorted(opts.concrete_fields + sortable_virtual_fields + opts.many_to_many))
            for key,value in new_attrs.items():
                value.label = fields[key].verbose_name
                value.help_text = fields[key].help_text
            attrs.update(new_attrs) 
            return super(BetterMetaClass, mcs).__new__(mcs, name, bases, attrs)   
    class BaseHOP(six.with_metaclass(BetterMetaClass, BaseModelForm)):
        pass
    class HOP(BaseHOP):
        class Meta:
            model = model_class
            exclude = ()
    return HOP

