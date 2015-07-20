# -*- coding: utf-8 -*-

from django.views import generic
from catalog.forms import ResourceSearchForm
from models import UserProfile
from catalog import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from registration.backends.default.views import RegistrationView
from django.core.urlresolvers import reverse

class HomeView(generic.TemplateView):
    """
    La page d'accueil principale
    """
    template_name =  'learningers/index.html'
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['search_form'] = ResourceSearchForm()
        context['latest_resources'] = models.Resource.objects.filter(public=True).order_by('-modified')[:5].select_subclasses()
        return context

class UserProfileView(generic.DetailView):
    """
    Consultation/modification d'un profil
    """
    template_name='registration/user_profile.html'
    model = UserProfile
    def get_object(self):
        qs = self.model.objects.filter(user__username=self.kwargs['slug'])
        if qs.exists():
            return qs.get()
        else:
            user = get_object_or_404(User,username=self.kwargs['slug'])
            return UserProfile.objects.create(user=user)
        
class CustomRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return reverse('registration_complete') + '?next=' + request.POST['next']
    
class CustomRegistrationCompleteView(generic.TemplateView):
    template_name = 'registration/registration_complete.html'
    def get_context_data(self, **kwargs):
        context = super(CustomRegistrationCompleteView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET['next']
        return context
    