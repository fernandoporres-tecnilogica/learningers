# -*- coding: utf-8 -*-
from inplaceeditform.fields import BaseAdaptorField

class AdaptorPhoneNumberField(BaseAdaptorField):

    @property
    def name(self):
        return 'phone_number'

    def render_value(self, field_name=None):
        value = super(AdaptorPhoneNumberField, self).render_value(field_name)
        return unicode(value)
