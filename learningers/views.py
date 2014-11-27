# -*- coding: utf-8 -*-

from django.views import generic
from catalog.forms import ResourceSearchForm
from models import UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class HomeView(generic.TemplateView):
    template_name =  'learningers/index.html'
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['search_form'] = ResourceSearchForm()
        return context

class UserProfileView(generic.DetailView):
    template_name='registration/user_profile.html'
    model = UserProfile
    def get_object(self):
        qs = self.model.objects.filter(user__username=self.kwargs['slug'])
        if qs.exists():
            return qs.get()
        else:
            user = get_object_or_404(User,username=self.kwargs['slug'])
            return UserProfile.objects.create(user=user)