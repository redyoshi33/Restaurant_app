from django.conf.urls import url
from . import views           
urlpatterns = [
    url(r'^main$', views.index),
    url(r'^dashboard$', views.dashboard),
    url(r'^register$', views.regis),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^profile$', views.profile),
    url(r'^profile/id$', views.profileid),
    url(r'^profile/edit$', views.editprofile),
    url(r'^profile/edit/submit$', views.editprofile),
    url(r'^group/(?P<id>\d+)$', views.group),
    url(r'^group/create$', views.groupcreate),
    url(r'^group/create/submit$', views.groupsubmit),
    url(r'^group/leave/(?P<id>\d+)$', views.groupleave),
    url(r'^delete/(?P<id>\d+)$', views.delete),
]