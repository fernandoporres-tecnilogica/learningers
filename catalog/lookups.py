from ajax_select import LookupChannel
import models
from django.contrib.auth.models import User
from haystack.query import SearchQuerySet
from django.utils.html import escape

class WayLookup(LookupChannel):
    model = models.Way
    search_field = 'name'
    def check_auth(self,request):
        pass

class LocationLookup(LookupChannel):
    model = models.GeoLocation
    search_field = 'address'
    def check_auth(self,request):
        pass
    
class UserLookup(LookupChannel):
    model = User
    search_field = 'username'
    def check_auth(self,request):
        pass        
    
class ResourceLookup(LookupChannel):
    "Lookup for autocompleting the main search query"
    model = models.Resource
    def get_query(self,q,request):
        print q
        return SearchQuerySet().autocomplete(name=q)
    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name
    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return escape(obj.name)
    def check_auth(self,request):
        pass    