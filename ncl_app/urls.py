from django.conf.urls import url
from . import views

app_name = 'ncl_app'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/regular_season/$', views.RegularSeasonView.as_view(), name='regular_season'),
    url(r'^(?P<pk>[0-9]+)/regular_season_day/$', views.RegularSeasonDayView.as_view(), name='regular_season_day'),
    url(r'^(?P<pk>[0-9]+)/regular_season_over/$', views.RegularSeasonOverView.as_view(), name='regular_season_over'),
    url(r'^(?P<pk>[0-9]+)/post_season_day/$', views.PostSeasonDayView.as_view(), name='post_season_day'),
]
