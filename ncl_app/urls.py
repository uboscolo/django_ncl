from django.conf.urls import url
from . import views

app_name = 'ncl_app'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<league_id>[0-9]+)/regular_season/$', views.regular_season, name='regular_season'),
    url(r'^(?P<league_id>[0-9]+)/regular_season_day/$', views.regular_season_day, name='regular_season_day'),
]
