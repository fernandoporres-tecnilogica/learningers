# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library
from django.conf import settings
from django.db.models.fields.related import RelatedField
register = Library()

@register.inclusion_tag("catalog/_render_field.html", takes_context=True)
def render_field(context, obj, field_name, field_verbosity=0, field_empty_value=settings.INPLACEEDIT_EDIT_EMPTY_VALUE, field_adaptor=""):
    print('hi bitch!')
    context['field_value'] = getattr(obj,field_name)
    context['obj'] = obj
    context['full_field_name'] = "obj." + field_name 
    context['field_verbosity'] = field_verbosity
    context['field_is_inplace_editable'] = False #obj._meta.fields[field_name].editable
    context['field_empty_value'] = field_empty_value
    context['field_adaptor'] = field_adaptor
    context['field_is_many'] = isinstance(getattr(obj,field_name),RelatedField)
    return context
