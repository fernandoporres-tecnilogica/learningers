#import django.contrib.admin
from django.contrib.gis import admin
from catalog import models
import reversion

class GeoLocationAdmin(reversion.VersionAdmin):
    pass

class ResourceAdmin(reversion.VersionAdmin):
    list_display = ('name', 'created','modified')
    pass

admin.site.register(models.GeoLocation, GeoLocationAdmin)     

for model in models.available_resource_models.values(): 
    admin.site.register(model, ResourceAdmin)


