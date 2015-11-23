# -*- coding: utf-8 -*-
"""
An annotation is a short comment attached to a specific range of a resource.
This comment can take several forms: text, sound, image, etc.
Depending on the resource, the concept of range takes different meanings.
For a textual resource, the range is a portion of the text,
for an audio resource, it is a time interval, etc.

Technically, an annotation is stored by combining two elements:
    - its "range" depends on the resource type to which it is attached.
    For example, for textual resources the range consists in certain portions of text,
    for audio resources it is a time interval, etc.
    - its "content", which can be textual, audio, image, etc.
"""
from __future__ import unicode_literals
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext as _
from model_utils.managers import InheritanceManager
from base import register_annotation_content, register_annotation_range
from django.contrib.auth.models import User

class Annotation(TimeStampedModel):
    """Generic model to hold the content of an annotation"""
    resource = models.ForeignKey('catalog.Resource',verbose_name=_(u"Ressource concernée"),related_name='annotations')
    authors = models.ManyToManyField(User,verbose_name=_(u'AuteurEs')) 
    links = models.ManyToManyField('catalog.Resource',verbose_name=_(u"Liens"),null=True,default=None)
    objects = InheritanceManager()

class Note(Annotation):
    """Annotation in the form of a short text"""
    text = models.CharField(max_length=1000,blank=True,verbose_name=_(u"Texte"))

# register annotation content types
register_annotation_content(Note)

class HtmlRange(models.Model):
    """
    A set of annotated ranges within an HTML document.
    This can be thought of as a set of selected words or sentences within the document,
    to which the annotation apply.
    """
    annotation = models.ForeignKey('catalog.Annotation',related_name='ranges')
    start = models.CharField(max_length=100)
    end = models.CharField(max_length=100)
    startOffset = models.IntegerField()
    endOffset = models.IntegerField()
    
class EventRange(models.Model):
    """
    A period of time to which an annotation applies. 
    """
    annotation = models.ForeignKey('catalog.Annotation',related_name='event_ranges')
    start = models.DateTimeField(_(u"Début"))
    end = models.DateTimeField(_(u"Fin"), help_text=_(u"La date de fin doit être postérieure à la date de début"))
    
# register annotation range types
register_annotation_range(HtmlRange)
register_annotation_range(EventRange)
