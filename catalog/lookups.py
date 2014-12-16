from ajax_select import LookupChannel
import models
from django.contrib.auth.models import User

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