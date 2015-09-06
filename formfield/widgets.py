from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
import re

class FormFieldWidget(forms.MultiWidget):
    """
    This widget will render each field found in the supplied form.
    """
    def __init__(self, fields, form_media, attrs=None):
        self.fields = fields
        self.form_media = form_media
        # Retreive each field widget for the form
        widgets = [f.widget for f in self.fields.values()]        
        super(FormFieldWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        N = len(name)
        subdata = dict( (k[N+1:],v) for k,v in  data.items() if k[0:N] == name)
        tmp = [ f.widget.value_from_datadict(subdata, files, k) for k,f in self.fields.items() ]
        return tmp 

    def render(self, name, value, attrs=None):
        if self.is_localized: 
            for widget in self.widgets: 
                widget.is_localized = self.is_localized 
        # value is a list of values, each corresponding to a widget 
        # in self.widgets. 
        if not isinstance(value, list): 
            value = self.decompress(value) 
        output = [] 
        final_attrs = self.build_attrs(attrs) 
        id_ = final_attrs.get('id', None) 
        for i, widget in enumerate(self.widgets): 
            try: 
                widget_value = value[i] 
            except IndexError: 
                widget_value = None 
            if id_: 
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i)) 
            output.append(widget.render(name + '.' + self.fields.keys()[i], widget_value, final_attrs)) 
        return mark_safe(self.format_output(attrs, output)) 
    
    def decompress(self, value):
        """
        Retreieve each field value or provide the initial values
        """
        if value:
            return [value.get(field.name, None) for field in self.fields.values()]
        return [field.initial for field in self.fields.values()]
        
    def format_label(self, field, id_, counter):
        """
        Format the label for each field
        """
        return '<label for="%s_%s" %s>%s</label>' % (
            id_, counter, field.required and 'class="required"', field.label)
            
    def format_help_text(self, field, counter):
        """
        Format the help text for the bound field
        """
        return '<span class="helptext">%s</span>' % unicode(field.help_text)
        
    def format_output(self, attrs, rendered_widgets):
        """
        This output will yeild all widgets grouped in a un-ordered list
        """
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)    
        ret = ['<ul class="formfield" %s>' %  flatatt(final_attrs)]
        for i, field in enumerate(self.fields.values()):
            label = self.format_label(field, id_, i)
            help_text = self.format_help_text(field, i)
            ret.append('<li>%s %s %s</li>' % (
                label, rendered_widgets[i], help_text))
            
        ret.append('</ul>')
        return u''.join(ret)
    
    def _get_media(self):
        "We need to also add the media defined directly in the form."
        return self.form_media + super(FormFieldWidget,self).media
    
    media = property(_get_media)
   
