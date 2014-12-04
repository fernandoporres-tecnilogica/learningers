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

class ResourceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = True
        kwargs['label_suffix'] = ''
        super(ResourceSearchForm, self).__init__(*args, **kwargs)
    q = forms.CharField(label=__(u'Quoi?'), initial='',required=True)
    a = AutoCompleteField('city',help_text='',label=__(u'Où?'), initial='',required=False)
    t = RecurrenceField(label=__(u'Quand?'), initial='',required=False,max_rdates=0,max_exdates=0)
    
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(ResourceSearchForm, self).search()
        address = self.cleaned_data.get('a')
        if(address):
            g = geocoders.Nominatim() # this should be changed to openstreetmap
            place, (lat, lng) = g.geocode(address)  
            print "%s: %.5f, %.5f" % (place, lat, lng)
        return sqs
    def no_query_found(self):
        return self.searchqueryset.all()

class GeoLocationForm(forms.ModelForm):
    "Formulaire pour la localisation"
    class Meta:
        model = GeoLocation
    
def make_resource_form(resource_type):
    model_class = available_resource_models[resource_type]
    class HOP(forms.ModelForm):
        description = forms.CharField(widget=MarkdownWidget())
        #parent = AutoCompleteSelectField('way',required=False,help_text=__(u'Tapez les premières lettres du parcours auquel vous souhaitez ajouter cette entrée'))
        class Meta:
            model = model_class
    # special handling of fields which should be inline
    if(hasattr(model_class,'geo')):
        HOP.geo = FormField(GeoLocationForm)
    if(hasattr(model_class,'picture')):
        HOP.picture = FormField(ImageForm)
    return HOP

