# -*- coding: utf-8 -*-
"""
URL dispatcher pour l'accès au catalogue.

Les URL sont construites de la facon suivante: 
list : lister les entrées du catalogue (utilisé seulement pendant le développement)
search : recherche dans le catalogue
resource-data : accès AJAX aux données d'une entrée (utilisé pour l'affichage ou la suppression)

$(type) : accès à une entrée.
L'URL est construite en agrégeant les slugs des parcours qui composent le chemin d'accès a la ressource
slug1/slug2/.../
puis le type de ressource
slug1/slug2/.../book
puis le slug de la ressource
slug1/slug2/.../book/harry-potter
"""
from django.conf.urls import patterns, url
from django.contrib import admin
from catalog import views
from models import available_resource_models

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^list/$', views.CatalogView.as_view(), name='list'),
    url(r'^search/$',  views.SearchResultsView.as_view(), name='search'),
    url(r'^search/data/$',  views.RequestMoreSearchResults.as_view(), name='search-data'),
#    url(r'^revert/$', views.ResourceRevertView.as_view(), name='revert'),
    url(r'^view/$', views.make_resource_view('way'), name='way-view'),
    url(r'^(?P<pk>\d+)/$', views.ResourceDetailView.as_view(), name='resource-data'),
    url(r'^create/$', views.CreateResourceView.as_view(), name='resource-create'),
    url(r'^calendar/(?P<pk>\d+)/(?P<size>(regular|small))$', views.CalendarRenderView.as_view(), name='calendar-data'),
)

for resource_type in available_resource_models:
    urlpatterns += patterns('',
                url('^create/' + resource_type + '/$', views.make_create_resource_view(resource_type), name=resource_type+'-create'),
                )

# parcours slug lookup
for i in range(0,4):
    p = r'^view/'
    for j in range(i):
        p += r'(?P<slug%d>[^/]+)/' % (i-j-1)
    urlpatterns += patterns('',url(p + r'(?P<slug>[^/]+)/$', views.make_resource_view('way'), name='way-view')) 
    # source slug lookup
    for resource_type in available_resource_models:
        if resource_type != 'way':  
            urlpatterns += patterns('', 
                    url(p + resource_type + '/(?P<slug>[^/]+)/$', views.make_resource_view(resource_type), name=resource_type + '-view'),
                    )

print urlpatterns