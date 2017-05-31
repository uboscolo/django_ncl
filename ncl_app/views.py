from django.shortcuts import get_object_or_404, render
from django.views import generic
import ncl_app.models as models

# Create your views here.


class IndexView(generic.ListView):
    """ Implements index view via a generic list view
        and by passing the first available league by name
    """
    # Class variables
    template_name = 'ncl_app/index.html'
    model = models.League


class RegularSeasonView(generic.DetailView):
    """ Implements regular season view via a generic detail view

    """
    # Class variables
    model = models.League
    template_name = 'ncl_app/regular_season.html'

    def get_context_data(self, **kwargs):
        """ returns the context data """
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        league.create_regular_season()
        context['schedule_list'] = models.Schedule.objects.all()
        return context


class RegularSeasonDayView(generic.DetailView):
    """ Implements regular season day view via a generic detail view

    """
    # Class variables
    model = models.League
    template_name = 'ncl_app/regular_season_day.html'

    def get_context_data(self, **kwargs):
        """ returns the context data """
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        completed = league.play_regular_season()
        if not completed:
            context['schedule_list'] = models.Schedule.objects.all()
        else:
            context['division_list'] = models.Division.objects.all()
        return context


class RegularSeasonOverView(generic.DetailView):
    """ Implements regular season over view via a generic detail view

    """
    # Class variables
    model = models.League
    template_name = 'ncl_app/regular_season_over.html'

    def get_context_data(self, **kwargs):
        """ returns the context data """
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        if league.postseason:
            league.create_post_season()
            context['schedule_list'] = models.Schedule.objects.all()
        return context


class PostSeasonDayView(generic.DetailView):
    """ Implements post season view via a generic detail view

    """
    # Class variables
    model = models.League
    template_name = 'ncl_app/post_season_day.html'

    def get_context_data(self, **kwargs):
        """ returns the context data """
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        league.play_post_season()
        context['schedule_list'] = models.Schedule.objects.all()
        return context
