# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from catalog.models.base import Resource,GeoLocation,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __

class Place(Resource):
    """Un lieu où on peut apprendre"""
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True,verbose_name=__(u'Localisation'), help_text=__(u'La localisation géographique du lieu'))
    class Meta:
        verbose_name =  __('Lieu')
        verbose_name_plural =  __('Lieux')
        
register_resource(Place)
