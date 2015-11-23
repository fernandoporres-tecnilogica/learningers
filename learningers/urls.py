# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from learningers import views
from django.views.generic import TemplateView
from django.contrib import admin
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

js_info_dict = {
    'packages': ('recurrence',),
}

urlpatterns = patterns('',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^charter/$', TemplateView.as_view(template_name='learningers/charter.html'), name='charter'),
    url(r'^about/$', TemplateView.as_view(template_name='learningers/about.html'), name='about'),
    url(r'^guide/0/$', TemplateView.as_view(template_name='learningers/guide.html'), name='guide'),
    url(r'^guide/1/$', views.Guide1View.as_view(), name='guide1'),
    url(r'^guide/2/$', TemplateView.as_view(template_name='learningers/guide2.html'), name='guide2'),
    url(r'^guide/3/$', TemplateView.as_view(template_name='learningers/guide3.html'), name='guide3'),
    # admin interface
    url(r'^admin/', include(admin.site.urls)),
    # user registration
    url(r'^accounts/register/$', views.CustomRegistrationView.as_view(), name='registration_register'),
    # short circuit to allow passing of "next" parameter to registration_complete template    
    url(r'^accounts/register/complete/$', views.CustomRegistrationCompleteView.as_view(), name='registration_complete'),
    url(r'^accounts/', include('registration.urls')),
    url(r'^profil/(?P<slug>[^/]+)/$', views.UserProfileView.as_view(), name='profil'),
    url(r'^convert/', include('lazysignup.urls')),
    # autocompletion
    url(r'^lookups/', include(ajax_select_urls)),
    # user-side translation
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),    
    # For language selector
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='lang')),
    # For in-place editing
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    # For testing calendars
    url(r'^schedule/', include('schedule.urls')),
    url(r'^markdown/', include('django_markdown.urls')),
    # Catalog browsing and search
    url(r'^catalog/', include('catalog.urls', namespace='catalog')),
)
