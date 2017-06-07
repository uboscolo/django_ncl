from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
import ncl_app.models as models

# Create your views here.


def create_regular_season(request, pk):
    """ Handles regular season creation 
    """
    league = get_object_or_404(models.League, pk=pk)
    league.create_regular_season()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('ncl_app:regular_season'))


def play_regular_season(request, pk):
    """ Handles regular season games
    """
    league = get_object_or_404(models.League, pk=pk)
    completed = league.play_regular_season()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    if completed:
        if league.postseason:
            league.create_post_season()
            return HttpResponseRedirect(reverse('ncl_app:post_season'))
        else:
            return HttpResponseRedirect(reverse('ncl_app:regular_season_over'))
    else:
        return HttpResponseRedirect(reverse('ncl_app:regular_season_day'))


class IndexView(generic.ListView):
    """ Implements index view via a generic list view
        and by passing the first available league by name
    """
    # Class variables
    template_name = 'ncl_app/index.html'
    model = models.League


class RegularSeasonView(generic.ListView):
    """ Implements regular season view via a generic list view

    """
    # Class variables
    template_name = 'ncl_app/regular_season.html'
    model = models.League


class RegularSeasonDayView(generic.ListView):
    """ Implements regular season day view via a generic list view

    """
    # Class variables
    template_name = 'ncl_app/regular_season_day.html'
    model = models.League


class RegularSeasonOverView(generic.ListView):
    """ Implements regular season over view via a generic list view

    """
    # Class variables
    template_name = 'ncl_app/regular_season_over.html'
    model = models.League


class PostSeasonDayView(generic.ListView):
    """ Implements post season day view via a generic list view

    """
    # Class variables
    template_name = 'ncl_app/post_season_day.html'
    model = models.League



#class RegularSeasonView(generic.DetailView):
#    """ Implements regular season view via a generic detail view
#
#    """
#    # Class variables
#    model = models.League
#    template_name = 'ncl_app/regular_season.html'
#
#    def get_context_data(self, **kwargs):
#        """ returns the context data """
#        context = super().get_context_data(**kwargs)
#        # league = context.get('league')
#        # league.create_regular_season()
#        context['schedule_list'] = models.Schedule.objects.all()
#        return context
