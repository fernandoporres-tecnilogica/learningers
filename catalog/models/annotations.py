# -*- coding: utf-8 -*-
"""
An annotation is a short comment attached to a specific range of a resource.
This comment can take several forms: text, sound, image, etc.
Depending on the resource, the concept of range takes different meanings.
For a textual resource, the range is a portion of the text,
for an audio resource, it is a time interval, etc.
"""
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext as _
from model_utils.managers import InheritanceManager
from base import register_annotation_content, register_annotation_range

class Annotation(TimeStampedModel):
    "Generic model to hold the content of an annotation"
    resource = models.ForeignKey('catalog.Resource',verbose_name=_(u"Ressource concernée"),related_name='annotations')
    links = models.ManyToManyField('catalog.Resource',verbose_name=_(u"Liens"),null=True,default=None)
    objects = InheritanceManager()

class Note(Annotation):
    "Annotation in the form of a short text"
    text = models.CharField(max_length=1000,blank=True,verbose_name=_(u"Texte"))

register_annotation_content(Note)

class HtmlRange(models.Model):
    annotation = models.ForeignKey('catalog.Annotation',related_name='ranges')
    start = models.CharField(max_length=100)
    end = models.CharField(max_length=100)
    startOffset = models.IntegerField()
    endOffset = models.IntegerField()
    
register_annotation_range(HtmlRange)