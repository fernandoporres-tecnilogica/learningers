# -*- coding: utf-8 -*-

from django.db import models
from commons.coding import classproperty
from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager
from forkit.models import ForkableModel
from django_languages.fields import LanguageField
from south.modelsinspector import add_introspection_rules
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as __
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from commons.signals import receiver_subclasses
from django.db.models.signals import post_save
from commons.templatetags.slug import deslugify#, wiki_slugify

import geopy
import reversion

# for GeoLocation
from django.contrib.gis.db.models import GeoManager, PointField
from geopy import geocoders
from django.contrib.gis.geos import fromstr

class ResourceLanguage(models.Model):
    code = LanguageField()
    @staticmethod
    def get_mycurrent():
        code = get_language().split('-')[0]
        language,created = ResourceLanguage.objects.get_or_create(code=code)
        return language        
    def __unicode__(self):
        
        return self.get_code_display()
    
add_introspection_rules([], ["^django_languages\.fields\.LanguageField"])

# Model of a generic resource in the catalog
class Resource(TimeStampedModel,ForkableModel):
    # Resource name
    name = models.CharField(max_length=200, verbose_name=__('Titre'))
    # Resource description
    description = models.CharField(max_length=1000, verbose_name=__('Description'),blank=True)
    # Resource parent
    parent = models.ForeignKey('catalog.Way',blank=True,null=True,default=None,related_name='children')
    # Resource slug
    slug = models.CharField(max_length=100,editable=False)  
    # Languages used in this resource
    languages = models.ManyToManyField(ResourceLanguage,editable=False)
    # Other entries related to this resource
    see_also = models.ManyToManyField('catalog.Resource',blank=True,null=True,default=None) 
    # Resource type
    resource_type = 'resource'
    # To manage inheritance
    objects = InheritanceManager()    
    
    def clean(self):
        pass
    def save(self,*args,**kwargs):
        if not self.pk:
            if not self.slug:
                self.slug = slugify(self.name)
        super(Resource, self).save(*args,**kwargs)
    # both slug and name should always be unique for a given resource type with a given parent
    def validate_unique(self,exclude=None):
        if self.__class__.objects.exclude(pk=self.pk).filter(slug=self.slug,parent=self.parent).exists():
            raise ValidationError({'slug':_(u'Une entrée du même slug et du même type existe déjà dans ce parcours.'),})
        if self.__class__.objects.exclude(pk=self.pk).filter(name=self.name,parent=self.parent).exists():
            raise ValidationError({'name':_(u'Une entrée du même nom et du même type existe déjà dans ce parcours.'),})
        super(Resource, self).validate_unique(exclude=exclude)
    # Stringify
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('catalog:resource', kwargs={'pk':self.pk})
    # return HTML code to display a small preview of this resource
    def preview(self):
        return self.description
    @classproperty
    def data_type(cls):
        return cls.resource_type
    @classproperty 
    def user_friendly_data_type(cls):
        return cls.user_friendly_type

class GeoLocation(models.Model):
    # Entry associated address
    address = models.CharField(max_length=200,verbose_name=__('Adresse'))
    # Entry associated location
    location = PointField(editable=False,default=fromstr("POINT(0 0)"),verbose_name=__(u'Coordonnées'))
    # manager
    objects = GeoManager()
    def save(self,*args,**kwargs):
        g = geocoders.Nominatim() # this should be changed to openstreetmap
        try:
            place, (lat,lng) = g.geocode(self.address)
            self.location = fromstr("POINT(%s %s)" % (lng, lat))
            self.address = place
        except TypeError:
            self.location = fromstr("POINT(0 0)")
        except geopy.exc.GeocoderServiceError:
            self.location = fromstr("POINT(0 0)")            
        super(GeoLocation, self).save(*args,**kwargs)                
    def __unicode__(self):
        return self.address

# A way is a resource composed of several other resources
class Way(Resource):
    user_friendly_type = __('Way')
    resource_type = 'way'
    help_text = __('Un parcours est une suite d\'étapes élémentaires correspondant à un apprentissage')
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True)
    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + self.slug + '/'
        elif not self.slug:
            return reverse('catalog:way')            
        else:
            return reverse('catalog:way', kwargs={'slug':self.slug})
    @staticmethod
    def make_from_slug(parent,slug):
        name = deslugify(slug)
        return Way(name=name,slug=slug,parent=parent)

# Model of a way which is attached to a session,
# to which resources created on-the-fly get attached by default
class SessionWay(Way):
    user = models.OneToOneField(User,related_name='way')
    def __init__(self, *args, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = _('Ton parcours')
        super(SessionWay, self).__init__(*args, **kwargs)
    def save(self,*args,**kwargs):
        if not self.pk:
            self.slug = ''
        super(SessionWay, self).save(*args,**kwargs) 
    def get_absolute_url(self):
        return reverse('catalog:way')

@receiver_subclasses(post_save, Resource,'resource-language')
def resource_post_save(sender,**kwargs):
    if kwargs['instance'].languages.count() == 0:
        kwargs['instance'].languages.add(ResourceLanguage.get_mycurrent())
        kwargs['instance'].save()



available_resource_models = dict((resource.resource_type,resource) for resource in (
                                                                           Way,
))

# register for version control
reversion.register(Resource)
for model in available_resource_models.values():
    reversion.register(model, follow=['resource_ptr'])