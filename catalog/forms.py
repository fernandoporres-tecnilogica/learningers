# -*- coding: utf-8 -*-

from haystack.forms import SearchForm
from recurrence.forms import RecurrenceField
from django import forms
from ajax_select.fields import AutoCompleteField
from geopy import geocoders
from django.utils.translation import ugettext_lazy as _

class ResourceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = True
        kwargs['label_suffix'] = ''
        super(ResourceSearchForm, self).__init__(*args, **kwargs)
    q = forms.CharField(label=_(u'Quoi?'), initial='',required=True)
    a = AutoCompleteField('city',help_text='',label=_(u'Où?'), initial='',required=False)
    t = RecurrenceField(label=_(u'Quand?'), initial='',required=False,max_rdates=0,max_exdates=0)
    
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