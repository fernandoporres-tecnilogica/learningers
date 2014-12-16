# -*- coding: utf-8 -*-

from catalog.models.base import Resource,GeoLocation,register_resource
from django.db import models
from schedule.models import Event
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.models import User

class MeetingResource(Resource,Event):
    """Un ou plusieurs évènements pendant lesquels des personnes se retrouvent pour agir, apprendre, échanger..."""
    user_friendly_type = __('Rencontre')
    resource_type = 'meeting'
    geo = models.ForeignKey(GeoLocation,default=None,null=True,blank=True,verbose_name=__(u'Où?'), help_text=__(u'Le lieu de rencontre'))
    participants = models.ManyToManyField(User)
    def save(self,*args,**kwargs):
        self.title = self.name
        self.calendar = self.parent.calendar
        super(MeetingResource, self).save(*args,**kwargs)   

register_resource(MeetingResource)