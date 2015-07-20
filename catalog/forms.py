# -*- coding: utf-8 -*-

from haystack.forms import SearchForm
from recurrence.forms import RecurrenceField
from recurrence.base import deserialize
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
from datetimewidget.widgets import DateTimeWidget
from django.forms.fields import DateTimeField
import geopy
from django.forms.widgets import HiddenInput
from datetime import datetime, timedelta
from imaging.forms import ImageForm

class ResourceSearchForm(SearchForm):
    """
    Main search form.
    
    Ordering of results is computed according to the following:
    
    """
    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = True
        kwargs['label_suffix'] = ''
        super(ResourceSearchForm, self).__init__(*args, **kwargs)
    #q = forms.CharField(label=__(u'Quoi?'), initial='',required=True)
    q = AutoCompleteField('resource',help_text='',label=__(u'Quoi?'), initial='',required=True)
    a = AutoCompleteField('location',help_text='',label=__(u'Où?'), initial='',required=False)
    t = RecurrenceField(label=__(u'Quand?'), initial='',required=False,max_rdates=0,max_exdates=0)
    d = forms.CharField(label=__(u'Quand?'), initial='',required=False)
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
                #sqs = sqs.dwithin('location',loc,max_dist).distance('location',loc)
            except geopy.exc.GeocoderServiceError:  
                pass
        time = self.cleaned_data.get('t')
        if(time):
            # extract serialized events from search query set index
            events = sqs.exclude(event='toto')
            excluded = list()
            for e in events:
                if e.event:
                    # we only check if we can go to the next upcoming occurrence
                    # checking all occurrences would be too costly
                    ev = deserialize(e.event).after(datetime.now())
                    if not ev in time.occurrences(dtstart = ev):
                        excluded.append(e.pk)
            if(excluded):
                sqs = sqs.exclude(id__in=excluded)
        return sqs
    def no_query_found(self):
        return self.searchqueryset.all()

class GeoLocationForm(forms.ModelForm):
    "Formulaire pour la localisation"
    class Meta:
        model = GeoLocation
        fields = ('address',)
       
def make_resource_form(resource_type):
    model_class = available_resource_models[resource_type]
    
    class BetterMetaClass(ModelFormMetaclass):
        def __new__(cls, name, bases, attrs):
            new_attrs = {}
            if(hasattr(model_class,'geo')):
                new_attrs['geo'] = FormField(GeoLocationForm,related=True)
            if(hasattr(model_class,'user')):
                new_attrs['user'] = AutoCompleteSelectField('user',required=False)
            if(hasattr(model_class,'avatar')):
                new_attrs['avatar'] = FormField(ImageForm,related=True,required=False)
            opts = model_class._meta
            # Avoid circular import
            from django.db.models.fields import Field as ModelField
            sortable_virtual_fields = [f for f in opts.virtual_fields
                                       if isinstance(f, ModelField)]
            fields = dict((f.name, f) for f in sorted(opts.concrete_fields + sortable_virtual_fields + opts.many_to_many))
            for key,value in new_attrs.items():
                value.label = fields[key].verbose_name
                value.help_text = fields[key].help_text
                value.required = (fields[key].blank == False and fields[key].null == False) 
            attrs.update(new_attrs) 
            return super(BetterMetaClass, cls).__new__(cls, name, bases, attrs)   
    class BaseHOP(six.with_metaclass(BetterMetaClass, BaseModelForm)):
        pass
    class HOP(BaseHOP):
        def __init__(self, *args, **kwargs):
            super(HOP, self).__init__(*args, **kwargs)
            self.fields['parent'].widget = HiddenInput()
            self.fields['description'].widget = MarkdownWidget()
            for field_name in self.fields:
                if isinstance(self.fields[field_name],DateTimeField):
                    self.fields[field_name].widget = DateTimeWidget(usel10n=True)
        class Meta:
            model = model_class
            exclude = ('title','creator','see_also','participants','calendar')
    return HOP

