from haystack import indexes
from catalog import models
from django.template.loader import render_to_string
import sys
from schedule.models import Event
from recurrence.base import from_dateutil_rrule, serialize, Recurrence

class ResourceIndexBase(indexes.SearchIndex):
    text = indexes.NgramField(document=True)
    rendered = indexes.CharField(indexed=False)
    name = indexes.EdgeNgramField(model_attr='name')
    def prepare_text(self,obj):
        return "%s %s" % (obj.name, obj.description)
    def prepare_rendered(self,obj):
        args = { 'resource_type': obj.resource_type, 
                 'resource_source': 'internal',
                 'resource_name': obj.name,
                 'resource_description' : obj.preview(),
                 'resource_tooltip' : obj.description,
                 'resource_url': obj.get_absolute_url(),
                }
        return render_to_string('catalog/resource.html',args)
    
def make_search_index(model):
    class EventResourceIndexBase(ResourceIndexBase):
        event = indexes.CharField(indexed=False)
        def prepare_event(self,obj):
            r = from_dateutil_rrule(obj.get_rrule_object())
            rec = Recurrence(dtstart = obj.start, rrules=[r])
            return serialize(rec)
    if issubclass(model,Event):
        HOP = EventResourceIndexBase
    else:
        HOP = ResourceIndexBase
    class WayResourceIndexBase(HOP):
        def index_queryset(self, using=None):
            "Used when the entire index for model is updated."
            return self.get_model().objects.exclude(pk__in=models.SessionWay.objects.values('pk')) # this is very rough
    if model is models.Way:
        HOP2 = WayResourceIndexBase
    else:
        HOP2 = HOP
    if hasattr(model,'geo'):
        class GeoResourceIndex(HOP2, indexes.Indexable):
            location = indexes.LocationField(model_attr='geo__location',null=True)
            def get_model(self):
                return model  
        return GeoResourceIndex
    else:            
        class ResourceIndex(HOP2, indexes.Indexable): 
            def get_model(self):
                return model
        return ResourceIndex               
            
for name, model in models.available_resource_models.iteritems():
    setattr(sys.modules[__name__],name + '_index', make_search_index(model))
      
        
