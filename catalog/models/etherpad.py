# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from catalog.models.base import Resource,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django import template
from django.template.defaultfilters import stringfilter
from urllib2 import HTTPError, URLError
register = template.Library()

from commons.string import upper_repl
import re
from etherpad_lite import EtherpadLiteClient
from urlparse import urlparse
from django.core.exceptions import ValidationError

@register.filter
@stringfilter
def pad_deslugify(string):
    result = re.sub(r'[-_]', ' ', string)
    result = re.sub(r'^(\w)',upper_repl, result)
    return result
 
@register.filter
@stringfilter
def pad_slugify(string):
    string = re.sub(r'^.+[:]','',string)
    string = re.sub(r'\s', '_', string)
    string = re.sub(r'^(\w)',upper_repl, string)
    return string

class Etherpad(Resource):
    """Un pad hébergé sur un serveur Etherpad."""
    padserver = models.URLField(verbose_name=__(u"URL du serveur"),help_text=__(u"Le serveur où est hébergé le pad, Example: http://lite4.framapad.org/"))
    padname = models.CharField(max_length=50,verbose_name=__(u"Identifiant du pad"),help_text=__(u"L'identifiant du pad sur le serveur"))

    class Meta:
        verbose_name = __('Pad Etherpad')
        verbose_name_plural = __('Pads Etherpad')
        
    def get_embed_url(self):
        return "http://" + self.padserver + '/p/' + pad_slugify(self.padname)
    
    def get_api_url(self):
        return "http://" + self.padserver + '/api/'
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.slug = self.padserver + '/p/' + pad_slugify(self.padname)  
    
    def preview(self):
        try:
            c = EtherpadLiteClient(base_url=self.get_api_url())
            data = c.getHTML(padID=self.padname)
            return data
        except (HTTPError, URLError):
            return super(Etherpad,self).preview()
        
    @staticmethod
    def make_from_slug(parent,slug):
        tokens = slug.split('/p/')
        if(len(tokens) != 2):
            print "bouh"
            print slug
            raise ValidationError(_("Impossible de reconstruire l'adresse du PAD correspondant à " + slug ))
        padname = pad_deslugify(tokens[1])
        return Etherpad(parent=parent,name=padname,slug=slug,padserver="http://" + tokens[0],padname=padname)

register_resource(Etherpad)
