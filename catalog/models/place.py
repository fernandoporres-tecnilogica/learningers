# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from catalog.models.base import Resource,GeoLocation,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __
from phonenumber_field.modelfields import PhoneNumberField


class Place(Resource):
    """Un lieu où on peut apprendre"""
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True,verbose_name=__(u'Localisation'), help_text=__(u'La localisation géographique du lieu'))
    phone_number = PhoneNumberField(null=True,blank=True,verbose_name=__(u'Téléphone'), help_text=__(u'Un numéro de téléphone fixe'))
    opening_times = models.CharField(max_length=200,blank=True,default='',verbose_name=__(u'Horaires'), help_text=__(u"Les horaires d'accueil du lieu") )
    @staticmethod
    def make_from_slug(parent,slug):
        return Place(parent=parent,geo=GeoLocation.make_from_slug(slug))
    def save(self,*args,**kwargs):
        if not self.pk:
            self.slug = self.geo.slug()
    class Meta:
        verbose_name =  __('Lieu')
        verbose_name_plural =  __('Lieux')
        
register_resource(Place)
