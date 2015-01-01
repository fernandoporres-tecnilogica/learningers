# -*- coding: utf-8 -*-

from catalog.models.base import Resource,GeoLocation,register_resource
from django.db import models
from schedule.models import Event
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.models import User

class Meeting(Resource,Event):
    """Un ou plusieurs évènements pendant lesquels des personnes se retrouvent pour agir, apprendre, échanger..."""
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True,verbose_name=__(u'Où?'), help_text=__(u'Le lieu de rencontre'))
    participants = models.ManyToManyField(User)
    class Meta:
        verbose_name =  __('Rencontre')
        verbose_name_plural =  __('Rencontres')    
    def save(self,*args,**kwargs):
        self.title = self.name
        self.calendar = self.parent.calendar
        super(Meeting, self).save(*args,**kwargs)   

register_resource(Meeting)