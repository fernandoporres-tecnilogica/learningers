# -*- coding: utf-8 -*-

from catalog.models.base import Resource,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

from commons.string import upper_repl
import re

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
        return self.padserver + 'p/' + pad_slugify(self.padname)
    
    def get_api_url(self):
        return self.padserver + 'api/'

register_resource(Etherpad)
