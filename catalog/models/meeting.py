# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from catalog.models.base import Resource,GeoLocation,register_resource
from catalog.models.place import Place
from django.db import models
from schedule.models import Event
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.models import User

class Meeting(Resource,Event):
    """Un ou plusieurs évènements pendant lesquels des personnes se retrouvent pour agir, apprendre, échanger..."""
    places = models.ManyToManyField(Place,verbose_name=__(u'Où?'), help_text=__(u'Lieu(x) de rendez-vous'))
    participants = models.ManyToManyField(User)
    mixite = models.CharField(max_length=50,default=__(u'Aucune'),blank=True,verbose_name=__(u'Non-mixité'), help_text=__(u'Régle de non-mixité'))
    class Meta:
        verbose_name =  __('Rencontre')
        verbose_name_plural =  __('Rencontres')    
    def save(self,*args,**kwargs):
        self.title = self.name
        self.calendar = self.parent.calendar
        super(Meeting, self).save(*args,**kwargs)

register_resource(Meeting)