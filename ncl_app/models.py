import random
from django.db import models

# Create your models here.


class League(models.Model):
    """ Implements a League object """

    # Class variables
    name = models.CharField(max_length=128)
    postseason = models.BooleanField(default=False)

    def __str__(self):
        """ __str__ overwrite """
        return self.name

    def create_regular_season(self):
        """ creates regular season by calling conferences method

        :return: None
        """
        for conference in self.conference_set.all():
            conference.create_regular_season()

    def create_post_season(self):
        """ creates post season by calling conferences method

        :return: None
        """
        for conference in self.conference_set.all():
            conference.create_post_season()

    def play_regular_season(self):
        """ plays regular season by calling conferences method

        :return: True or False if completed
        :rtype: bool
        """
        completed = False
        for conference in self.conference_set.all():
            completed = conference.play_regular_season() or completed

        return completed

    def play_post_season(self):
        """ plays post season by calling conferences method

        :return: True or False if completed
        :rtype: bool
        """
        pass


class Conference(models.Model):
    """ Implements a Conference object """

    # Class variables
    name = models.CharField(max_length=128)
    league = models.ForeignKey(League)

    def __str__(self):
        """ __str__ overwrite """
        return self.name

    def create_regular_season(self):
        """ creates regular season by calling division method

        :return: None
        """
        for division in self.division_set.all():
            division.create_regular_season_schedule()

    def create_post_season(self):
        """ creates post season by calling conferences method

        :return: None
        """
        for division in self.division_set.all():
            division.create_post_season_schedule()

    def play_regular_season(self):
        """ plays regular season by calling division method

        :return: True or False if completed
        :rtype: bool
        """
        completed = False
        for division in self.division_set.all():
            completed = division.play_regular_season_schedule() or completed

        return completed


class Schedule(models.Model):
    """ Implements a Schedule object """

    # Class variables
    name = models.CharField(max_length=128)
    current_day = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        """ __str__ overwrite """
        return self.name

    @property
    def sorted_day_set(self):
        """ returns in order days """
        return self.day_set.order_by('number')

    @property
    def get_current_day(self):
        """ returns current day """
        return self.day_set.get(number=self.current_day)

    @property
    def get_division(self):
        """ returns division """
        return self.division_set.get(name=self.name)

    def reset(self):
        """ resets schedule """
        self.current_day = 0
        self.completed = False
        self.save()
        self.day_set.all().delete()
        self.series_set.all().delete()

    def create_regular_season(self, team_list):
        """ creates a regular season schedule
            It first arranges all the division's team into a rotating table
            that is used to create a round robin schedule.
            It then rolls through the number of days that would make a round
            robin schedule and creates one day for the first part of the season
            and the associated day for the second half of the season (i.e.
            home and away teams are swapped)
            It uses the rotating table to fill out matches accordingly.

        :param team_list: List of teams
        :return: None
        """

        rotating_table = {}
        for team_idx in range(0, len(team_list)):
            rotating_table[team_idx + 1] = team_list[team_idx]
            team_idx += 1
        day_number = 1

        swapping = False
        while day_number <= len(team_list) - 1:
            # Create a new day, first half of the season
            first_half_day = Day(number=day_number, schedule=self)
            first_half_day.save()
            # Create a new day, second half of the season
            second_half_day_number = day_number + len(team_list) - 1
            second_half_day = Day(number=second_half_day_number, schedule=self)
            second_half_day.save()
            # Find teams and create Matches
            match_idx = 1
            while match_idx <= len(team_list) // 2:
                if match_idx == 1:
                    if swapping:
                        team1 = rotating_table[match_idx + 1]
                        team2 = rotating_table[match_idx]
                    else:
                        team1 = rotating_table[match_idx]
                        team2 = rotating_table[match_idx + 1]
                else:
                    team1 = rotating_table[match_idx + 1]
                    team2 = rotating_table[len(team_list) - match_idx + 2]
                # first half of the season
                first_half_match = Match(day=first_half_day)
                first_half_match.save()
                first_half_match_home_team_part = MatchPart(team=team1, match=first_half_match, location='home')
                first_half_match_home_team_part.save()
                first_half_match_away_team_part = MatchPart(team=team2, match=first_half_match, location='away')
                first_half_match_away_team_part.save()
                # second half of the season
                second_half_match = Match(day=second_half_day)
                second_half_match.save()
                second_half_match_home_team_part = MatchPart(team=team2, match=second_half_match, location='home')
                second_half_match_home_team_part.save()
                second_half_match_away_team_part = MatchPart(team=team1, match=second_half_match, location='away')
                second_half_match_away_team_part.save()
                match_idx += 1
            day_number += 1
            swapping = not swapping
            # rotate table
            curr_val = 0
            for entry in rotating_table.keys():
                if entry == 2:
                    curr_val = rotating_table[entry]
                    rotating_table[entry] = rotating_table[len(team_list)]
                elif entry > 2:
                    stored_val = rotating_table[entry]
                    rotating_table[entry] = curr_val
                    curr_val = stored_val

    def create_post_season_series(self, team_list):
        """ creates a playoffs/playouts schedule
            Teams are arranged such that the best team plays against the worst team as per
            regular season results.
            Series are created for team pairs in team list, then schedules are created per series

        :param team_list: List of teams
        :return: None
        """
        for team_idx in range(0, len(team_list) // 2):
            team_pair = [team_list[team_idx], team_list[len(team_list) - 1 - team_idx]]
            new_series = Series(schedule=self)
            new_series.save()
            new_series_home_team_part = SeriesPart(team=team_pair[0], series=new_series, lead=True)
            new_series_home_team_part.save()
            new_series_away_team_part = SeriesPart(team=team_pair[1], series=new_series, lead=False)
            new_series_away_team_part.save()
            home_selector = True
            for day_number in range(1, int(new_series.length) + 1):
                try:
                    new_day = self.day_set.get(number=day_number)
                except Day.DoesNotExist:
                    new_day = Day(number=day_number, schedule=self)
                    new_day.save()
                new_match = Match(day=new_day)
                new_match.save()
                home_team = new_series.seriespart_set.get(lead=home_selector).team
                new_match_home_team_part = MatchPart(team=home_team, match=new_match, location='home')
                new_match_home_team_part.save()
                away_team = new_series.seriespart_set.get(lead=not home_selector).team
                new_match_away_team_part = MatchPart(team=away_team, match=new_match, location='away')
                new_match_away_team_part.save()
                new_series.matches.add(new_match)
                new_series.save()
                home_selector = not home_selector
            self.save()

    def play_regular_season(self, match_phase="regular_time"):
        """ plays a regular season schedule
            It selects the next day in the schedule until the schedule is
            completed and plays all day's matches.
            When a match is played, first the teams' strenghts are gathered,
            second a home advantage is applied (if needed),
            third a "luck factor" is computed by drawing random numbers,
            Now strengths are adjusted according to the above factors and
            normalized, such that a decision can be taken if the match
            ended with a home team victory, loss or a draw.
            A score is also generated by looking up a score distribution table

        :param match_phase: phase of the match, e.g. regular time, extra time

        :return:
        """

        if self.current_day:
            self.current_day += 1
        else:
            self.current_day = 1
        self.save()
        # Play all matches in the selected day
        try:
            day = self.day_set.get(number=self.current_day)
        except Day.DoesNotExist:
            self.completed = True
            self.save()
        else:
            for match in day.match_set.all():
                # 1) get strengths
                strength1 = float(match.home_team.strength)
                strength2 = float(match.away_team.strength)
                # 2) apply home advantage
                if match.home_advantage:
                    strength1 *= 2
                # 3) Luck factor
                strength1 = random.uniform(0, strength1)
                strength2 = random.uniform(0, strength2)
                # Normalize Strength
                total_strength = strength1 + strength2
                rel_strength1 = strength1 / total_strength
                rel_strength2 = strength2 / total_strength
                rel_strength_ratio = rel_strength1 / rel_strength2
                # Take decision
                if rel_strength_ratio > 2:
                    match.outcome = '1'
                    match.home_team.update_points(3)
                elif rel_strength_ratio < 0.5:
                    match.outcome = '2'
                    match.away_team.update_points(3)
                else:
                    match.outcome = 'X'
                    match.home_team.update_points(1)
                    match.away_team.update_points(1)
                # Generate score based on results
                score = match.generate_score(match_phase=match_phase, match_result=match.outcome)
                match.score = score
                match.save()


class Division(models.Model):
    """ Implements a Division object """

    # Class variables
    name = models.CharField(max_length=128)
    conference = models.ForeignKey(Conference)
    schedule = models.ForeignKey(Schedule)

    def __str__(self):
        """ __str__ overwrite """
        return self.name

    @property
    def sorted_team_set(self):
        """ returns a list of teams in a descending order by points"""
        return self.team_set.order_by('points').reverse()

    def create_regular_season_schedule(self):
        """ creates regular season schedule
            It first reset all teams' points, then resets the schedule

        :return: None
        """
        for team in self.team_set.all():
            team.reset()
        self.schedule.reset()
        self.schedule.create_regular_season(self.team_set.all())

    def create_post_season_schedule(self):
        """ creates post season schedule

        :return: None
        """
        self.schedule.reset()
        self.schedule.create_post_season_series(self.team_set.filter(playoffs=True))
        self.schedule.create_post_season_series(self.team_set.filter(playoffs=False))

    def play_regular_season_schedule(self):
        """ plays regular season schedule

        :return: True/False if schedule is completed
        :rtype: bool
        """
        self.schedule.play_regular_season()
        completed = self.schedule.completed

        if completed:
            for team in self.sorted_team_set[0:len(self.sorted_team_set) // 2]:
                team.playoffs = True
                team.save()

        return completed


class Team(models.Model):
    """ Implements a Team object """

    # Class variables
    name = models.CharField(max_length=128)
    points = models.IntegerField(default=0)
    playoffs = models.BooleanField(default=False)
    strength = models.DecimalField(max_digits=7, decimal_places=4)
    division = models.ForeignKey(Division)

    def __str__(self):
        """ __str__ overwrite """
        return self.name

    def update_points(self, value):
        """ update points

        :param value: points
        :return: None
        """
        self.points += value
        self.save()

    def reset(self):
        """ reset """
        self.points = 0
        self.playoffs = False
        self.save()


class Day(models.Model):
    """ Implements a Day object """

    # Class variables
    number = models.IntegerField(default=0)
    schedule = models.ForeignKey(Schedule)

    def __str__(self):
        """ __str__ overwrite """
        return self.schedule.name + " - Day " + str(self.number)


class Match(models.Model):
    """ Implements a Match object """

    # Class variables
    OUTCOMES = (
        ('X', 'draw'),
        ('1', 'home'),
        ('2', 'away'),
    )
    teams = models.ManyToManyField(Team, through='MatchPart')
    day = models.ForeignKey(Day)
    score = models.CharField(max_length=10, default='0-0')
    outcome = models.CharField(max_length=1, choices=OUTCOMES, null=True)
    home_advantage = models.BooleanField(default=True)

    class Meta:
        """ Meta class """
        verbose_name_plural = "Matches"

    def __str__(self):
        """ __str__ overwrite """
        return "Day " + str(self.day.number) + " - " + self.home_team.name + " vs. " + self.away_team.name

    @property
    def home_team(self):
        """ returns the home team """
        return self.matchpart_set.get(location='home').team

    @property
    def away_team(self):
        """ returns the home team """
        return self.matchpart_set.get(location='away').team

    @staticmethod
    def generate_score(match_phase, match_result):
        """ generates the score
            The user would pass a match phase (i.e. regular time or extra time)
            and a math result in terms of home victory, loss or draw
            Based on the two inputs a probable score is genrated and returned

        :param match_phase: a string with either regular or extra time
        :param match_result: a string with 'X' (draw), '1' or '2' (home or away victory)
        :return: a string with the score
        :rtype: str
        """

        reglr_time_home = {'1-0': 0.125, '2-0': 0.090, '2-1': 0.093, '3-0': 0.045,
                           '4-0': 0.025, '3-1': 0.045, '3-2': 0.020, '4-1': 0.015,
                           '5-0': 0.005, '4-2': 0.007, '5-1': 0.005, '6-0': 0.002,
                           '4-3': 0.003, '5-2': 0.001, '6-1': 0.001, '7-0': 0.001}
        reglr_time_away = {'0-1': 0.065, '0-2': 0.050, '1-2': 0.053, '0-3': 0.015,
                           '0-4': 0.015, '1-3': 0.025, '2-3': 0.015, '1-4': 0.010,
                           '0-5': 0.003, '2-4': 0.002, '1-5': 0.002, '0-6': 0.001,
                           '3-4': 0.002, '2-5': 0.001, '1-6': 0.001, '0-7': 0.001}
        reglr_time_draw = {'0-0': 0.085, '1-1': 0.120, '2-2': 0.045, '3-3': 0.007}

        extra_time_home = {'1-0': 0.150, '2-0': 0.115, '2-1': 0.110, '3-0': 0.070}
        extra_time_away = {'0-1': 0.095, '0-2': 0.075, '1-2': 0.080, '0-3': 0.040}
        extra_time_draw = {'0-0': 0.120, '1-1': 0.145}

        lookup_tables = {('regular_time', '1'): reglr_time_home,
                         ('regular_time', '2'): reglr_time_away,
                         ('regular_time', 'X'): reglr_time_draw,
                         ('extra_time', '1'): extra_time_home,
                         ('extra_time', '2'): extra_time_away,
                         ('extra_time', 'X'): extra_time_draw}

        # Move in __init__
        lookup_table = lookup_tables[(match_phase, match_result)]
        total = 0
        for prob in lookup_table.values():
            total += prob

        roll = random.uniform(0, total)

        current_val = 0
        for res, prob in lookup_table.items():
            current_val += prob
            if roll <= current_val:
                return res


class MatchPart(models.Model):
    """ Implements a Match Part object """

    # Class variables
    team = models.ForeignKey(Team)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    location = models.CharField(max_length=4)
    # winner = models.BooleanField(null=True, blank=True)

    def __str__(self):
        """ __str__ overwrite """

        return self.team.name + " in " + self.match.__str__()


class Series(models.Model):
    """ Implements a Match object """

    # Class variables
    teams = models.ManyToManyField(Team, through='SeriesPart')
    matches = models.ManyToManyField(Match)
    length = models.IntegerField(default=3)
    schedule = models.ForeignKey(Schedule)

    class Meta:
        """ Meta class """
        verbose_name_plural = "Series"

    def __str__(self):
        """ __str__ overwrite """
        return self.lead_team.name + " vs. " + self.non_lead_team.name + " - best of " + str(self.length)

    @property
    def lead_team(self):
        """ returns the home team """
        return self.seriespart_set.get(lead=True).team

    @property
    def non_lead_team(self):
        """ returns the home team """
        return self.seriespart_set.get(lead=False).team


class SeriesPart(models.Model):
    """ Implements a Series Part object """

    # Class variables
    team = models.ForeignKey(Team)
    series = models.ForeignKey(Series)
    lead = models.BooleanField(default=False)
    # winner = models.BooleanField(null=True, blank=True)

    def __str__(self):
        """ __str__ overwrite """

        return self.team.name + " in " + self.series.__str__()
