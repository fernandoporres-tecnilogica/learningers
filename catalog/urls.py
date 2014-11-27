from django.conf.urls import patterns, url
from django.contrib import admin
from catalog import views
from models import available_resource_models

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^list/$', views.CatalogView.as_view(), name='list'),
    url(r'^search/$',  views.CatalogView.as_view(), name='search'),
#    url(r'^revert/$', views.ResourceRevertView.as_view(), name='revert'),
    url(r'^view/$', views.make_resource_view('way'), name='way'),
    url(r'^(?P<pk>\d+)/$', views.ResourceDetailView.as_view(), name='resource-detail'),
)

# parcours slug lookup
for i in range(0,4):
    p = r'^view/'
    for j in range(i):
        p += r'(?P<slug%d>[^/]+)/' % (i-j-1)
    urlpatterns += patterns('',url(p + r'(?P<slug>[^/]+)/$', views.make_resource_view('way'), name='way')) 
    # source slug lookup
    for resource_type in available_resource_models:
        urlpatterns += patterns('', 
                url(p + resource_type + '/(?P<slug>.+)/$', views.make_resource_view(resource_type), name=resource_type),
  #              url(p + resource_type + '/(?P<slug>.+)/(?P<revpk>\d+)/$', views.make_resource_view(resource_type), name=resource_type),
                )

