from learningers.models import UserProfile
from django.contrib.auth.models import User

class MyAdaptorEditInline(object):
    @classmethod
    def can_edit(cls, adaptor_field):
        obj = adaptor_field.obj
#        print obj.__class__
        if isinstance(obj,UserProfile):
            if adaptor_field.request.user is obj.user:
                return True
            else:
                return False
        if isinstance(obj,User):
            if adaptor_field.request.user is obj:
                return True
            else:
                return False
        return True