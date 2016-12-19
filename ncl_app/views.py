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

    def get_queryset(self):
        """
        Returns a list of one league

        :return: list of one league ordered by name
        :rtype: list
        """
        return models.League.objects.order_by('-name')[:1]


def regular_season(request, league_id):
    """ Implements regular season view by rolling through all
        league's conferences and divisions and by creating a
        regular season schedule and filling it out with days and matches.
        Returns HttpResponse whose content is the regular season schedule
        day by day

    :param request: HTTP request
    :param league_id: league identifier
    :return: HttpResponse with regular season schedule
    :rtype: HttpResponse object
    """

    league = get_object_or_404(models.League, pk=league_id)
    for conference in league.conference_set.all():
        for division in conference.division_set.all():
            division.create_regular_season_schedule()

    context = {'schedule_list': models.Schedule.objects.all(), 'league': league}
    return render(request, 'ncl_app/regular_season.html', context)


def regular_season_day(request, league_id):
    """ Implements regular season day view by rolling through all
        league's conferences and divisions and by playing a
        regular season schedule.
        Returns HttpResponse whose content is the current day with
        matches' results and updated table


    :param request: HTTP request
    :param league_id: league identifier
    :return: HttpResponse with regular season's current day results
    :rtype: HttpResponse object
    """
    league = get_object_or_404(models.League, pk=league_id)
    for conference in league.conference_set.all():
        for division in conference.division_set.all():
            division.play_regular_season_schedule()

    context = {'schedule_list': models.Schedule.objects.all(), 'league': league}
    return render(request, 'ncl_app/regular_season_day.html', context)
