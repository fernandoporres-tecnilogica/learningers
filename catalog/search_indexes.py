from haystack import indexes
from catalog import models
from django.template.loader import render_to_string
import sys

class ResourceIndexBase(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    rendered = indexes.CharField(indexed=False)
    def prepare_text(self,obj):
        return "%s %s" % (obj.name, obj.description)
    def prepare_rendered(self,obj):
        args = { 'resource_type': obj.resource_type, 
                 'data_type' : obj.data_type,
                 'resource_source': 'internal',
                 'resource_name': obj.name,
                 'resource_description' : obj.preview(),
                 'resource_tooltip' : obj.description,
                 'resource_url': obj.get_absolute_url(),
                }
        return render_to_string('catalog/resource.html',args)
        
def make_search_index(model):
    if hasattr(model,'geo'):
        class GeoResourceIndex(ResourceIndexBase, indexes.Indexable):
            location = indexes.LocationField(model_attr='geo__location',null=True)
            def get_model(self):
                return model  
        return GeoResourceIndex
    else:            
        class ResourceIndex(ResourceIndexBase, indexes.Indexable): 
            def get_model(self):
                return model
        return ResourceIndex               
            
for name, model in models.available_resource_models.iteritems():
    setattr(sys.modules[__name__],name + '_index', make_search_index(model))
      
        
