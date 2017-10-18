from django.conf.urls import url

from . import views

app_name = 'weather'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    # url(r'^subscribe/result/$', views.result, name='result'),
]
