'''
Created on 28 janv. 2014

@author: rnguyen
'''
import models
from lazysignup.decorators import allow_lazy_user

class ParcoursSessionMiddleware(object):
    def process_request(self,request):
        if(request.is_ajax()):
            return None
        @allow_lazy_user
        def dummy(request):
            pass
        dummy(request)
        if not models.SessionWay.objects.filter(user=request.user).exists(): 
            user_parcours = models.SessionWay(user=request.user)
            user_parcours.save()
        request.way = models.SessionWay.objects.get(user=request.user)
        request.session['way'] = request.way.pk
