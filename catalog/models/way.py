# -*- coding: utf-8 -*-
from catalog.models.base import Resource, register_resource
from django.db import models
from schedule.models import Calendar
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from commons.templatetags.slug import deslugify
from django.utils import timezone
import pytz
from schedule.periods import Month
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as __
from django.utils.text import slugify
from catalog.models.meeting import MeetingResource
from django.db.models import Q
from schedule.models import Event

# A way is a resource composed of several other resources
class Way(Resource):
    """Une ressource composée d'une suite d'autres ressources à consulter dans un certain ordre pour parvenir à un apprentissage."""
    user_friendly_type = __('Parcours')
    resource_type = 'way'
    calendar = models.OneToOneField(Calendar,editable=False,verbose_name=__('Agenda'),help_text=__("Le calendrier des rencontres associées à ce parcours"))
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
    def save(self,*args,**kwargs):
        if not self.pk:
            if not hasattr(self,'calendar'):
                if not self.slug:
                    self.slug = slugify(self.name) 
                calendar = Calendar(name=self.name,slug=self.slug)
                calendar.save()
                setattr(self,'calendar',calendar)
        super(Way, self).save(*args,**kwargs)
    def get_events(self):
        meetings = MeetingResource.objects.filter(Q(parent=self.pk)|Q(parent__parent=self.pk)|Q(parent__parent__parent=self.pk)).values_list('event_ptr',flat=True)
        return Event.objects.filter(pk__in=list(meetings))
    def get_month(self,date=None):
        if date is None:
            date = timezone.now()
        local_timezone = pytz.timezone('UTC')
        return Month(self.get_events(), date, None, None, local_timezone)
                            
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

register_resource(Way)