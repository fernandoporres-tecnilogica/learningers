from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

def upper_repl(match):
    return match.group(1).upper()
 
@register.filter
@stringfilter
def deslugify(string):
    result = re.sub(r'[-_]', ' ', string)
    result = re.sub(r'^(\w)',upper_repl, result)
    return result
 
@register.filter
@stringfilter
def slugify(string):
    string = re.sub(r'^.+[:]','',string)
    string = re.sub(r'\s', '_', string)
    string = re.sub(r'^(\w)',upper_repl, string)
    return string
