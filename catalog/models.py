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
from schedule.models import Event 

import geopy
import reversion

# for GeoLocation
from django.contrib.gis.db.models import GeoManager, PointField
from geopy import geocoders
from django.contrib.gis.geos import fromstr
from django.http.response import Http404

class ResourceLanguage(models.Model):
    """
    Une langue utilisée dans une ou plusieurs resources répertoriées
    """
    code = LanguageField()
    @staticmethod
    def get_mycurrent():
        "Retourne la langue actuellement utilisée pour la session en cours"
        code = get_language().split('-')[0]
        language,created = ResourceLanguage.objects.get_or_create(code=code)
        return language        
    def __unicode__(self):
        "Retourne le nom de la langue"
        return self.get_code_display()
    
add_introspection_rules([], ["^django_languages\.fields\.LanguageField"])

class Resource(TimeStampedModel,ForkableModel):
    """
    Modèle abstrait de base pour les resources répertoriées dans le catalogue.
    
    Les modèles correspondant aux différents types de resources dérivent de celui-ci.
    """
    # Resource name
    name = models.CharField(max_length=200, verbose_name=__('Titre'), help_text=__(u'Le nom de la ressource dans le répertoire'))
    # Resource description
    description = models.CharField(max_length=1000, verbose_name=__('Description'),blank=True, help_text=__(u'Une brève description du contenu de la ressource'))
    # Resource parent
    parent = models.ForeignKey('catalog.Way',blank=True,null=True,default=None,related_name='children', help_text=__('Le parcours dont cette ressource fait partie'))
    # Resource slug
    slug = models.CharField(max_length=100,editable=False)  
    # Languages used in this resource
    languages = models.ManyToManyField(ResourceLanguage,editable=False, help_text=__(u'Les langues à maîtriser pour comprendre cette ressource'))
    # Other entries related to this resource
    see_also = models.ManyToManyField('catalog.Resource',verbose_name=__('Voir aussi'),blank=True,null=True,default=None, help_text=__(u"D'autres resources liées à celle-ci")) 
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
        if self.parent:
            return self.parent.get_absolute_url() + self.resource_type + '/' + self.slug + '/'
        else:
            raise Http404
    def preview(self):
        "return HTML code to display a small preview of this resource"
        return self.description
    @classproperty
    def data_type(cls):
        "L'identifiant du type de données contenu dans cette ressource"
        return cls.resource_type
    @classproperty 
    def user_friendly_data_type(cls):
        "La description du type de données contenu dans cette ressource"
        return cls.user_friendly_type

class GeoLocation(models.Model):
    """
    La localisation géographique d'une ressource
    """
    # Entry associated address
    address = models.CharField(max_length=200,verbose_name=__('Adresse'),help_text=__("L'adresse postale du lieu"))
    # Entry associated location
    location = PointField(editable=False,default=fromstr("POINT(0 0)"),verbose_name=__(u'Coordonnées'),help_text=__("Les coordonnées GPS du lieu"))
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
    """
    Un parcours est une ressource composée d'une suite d'autres ressources à consulter dans un certain ordre
    pour parvenir à un apprentissage.
    """
    user_friendly_type = __('Parcours')
    resource_type = 'way'
    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + self.slug + '/'
        elif not self.slug:
            return reverse('catalog:way-view')            
        else:
            return reverse('catalog:way-view', kwargs={'slug':self.slug})
    @staticmethod
    def make_from_slug(parent,slug):
        name = deslugify(slug)
        return Way(name=name,slug=slug,parent=parent)

class SessionWay(Way):
    """
    Model of a way which is attached to a session,
     to which resources created on-the-fly get attached by default
    """
    user = models.OneToOneField(User,related_name='way',help_text=__(u"L'utilisateur.rice propriétaire de la session"))
    def __init__(self, *args, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = _('Ton parcours')
        super(SessionWay, self).__init__(*args, **kwargs)
    def save(self,*args,**kwargs):
        if not self.pk:
            self.slug = ''
        super(SessionWay, self).save(*args,**kwargs) 

class Initiative(Resource):
    """
    Resource based on some real-life initiative of individuals or groupes of people.
    """
    user_friendly_type = __('Initiative')
    resource_type = 'initiative'
    help_text = __('Une initiative est un évènement ou une séquence de plusieurs évènements pendant lesquels des personnes se rencontrent pour apprendre.')
    event = models.OneToOneField(Event)
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True)
    #participants = models.ManyToManyField('catalog.HumanSource')
    def save(self,*args,**kwargs):
        if not self.name:
            self.name = self.event.title
        self.event.description = self.description
        super(Initiative, self).save(*args,**kwargs)        
    pass

@receiver_subclasses(post_save, Resource,'resource-language')
def resource_post_save(sender,**kwargs):
    if kwargs['instance'].languages.count() == 0:
        kwargs['instance'].languages.add(ResourceLanguage.get_mycurrent())
        kwargs['instance'].save()

available_resource_models = dict((resource.resource_type,resource) for resource in (
                                                                           Way, Initiative
))

# register for version control
reversion.register(Resource)
for model in available_resource_models.values():
    reversion.register(model, follow=['resource_ptr'])