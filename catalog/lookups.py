from ajax_select import LookupChannel
import models
import cities.models

class WayLookup(LookupChannel):
    model = models.Way
    search_field = 'name'
    def check_auth(self,request):
        pass
