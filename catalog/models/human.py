# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from catalog.models.base import Resource,GeoLocation,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __

class Human(Resource):
    """Une personne susceptible de contribuer à un apprentissage."""
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True,verbose_name=__(u'Adresse physique'), help_text=__(u'Le lieu où se trouve la personne'))
    email = models.EmailField(blank=True,verbose_name=__(u'Adresse électronique'), help_text=__(u"Une adresse où joindre cette personne"))
    user = models.ForeignKey('auth.User',default=None,null=True,blank=True,verbose_name=__(u'Identifiant'),help_text=__(u"L'identifiant du compte associé à cette personne si elle en possède un"))
    class Meta:
        verbose_name =  __('Humain-e')
        verbose_name_plural =  __('Humain-e-s')
        
    def save(self,*args,**kwargs):
        if not self.pk and not self.name and self.user:
            self.name = self.user.username
        super(Human, self).save(*args,**kwargs) 

register_resource(Human)
