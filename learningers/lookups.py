from ajax_select import LookupChannel
import cities.models
 
class CityLookup(LookupChannel):
    model = cities.models.City
    search_field = 'name'
    def check_auth(self,request):
        pass
    