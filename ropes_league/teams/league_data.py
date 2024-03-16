import numpy as np
import pandas as pd

from ..league_data import LeagueData, prep_grade
from . import scoring

GRADE_DIFFICULTY = {
    "X": np.nan,
    "5.7": 0,
    "5.8": 1,
    "5.9": 2,
    "5.10-": 3,
    "5.10": 4,
    "5.10+": 5,
    "5.11-": 6,
    "5.11": 7,
    "5.11+": 8,
    "5.12-": 9,
    "5.12": 10,
    "5.12+": 11,
    "5.13-": 12,
    "5.13": 13,
    "5.13+": 14,
}


class TeamLeagueData(LeagueData):

    def climbers(self):
        return self.make_dataframe("Climbers", "id").assign(
            grade=lambda df: prep_grade(df.grade),
            difficulty=lambda df: df.grade.replace(GRADE_DIFFICULTY),
        )

    def teams(self):
        return self.make_dataframe("Teams", "id")

    def climbs(self, week: int):
        return self.make_dataframe(f"Week {week} Climbs").assign(
            grade_1=lambda df: prep_grade(df.grade_1),
            difficulty_1=lambda df: df.grade_1.replace(GRADE_DIFFICULTY),
            grade_2=lambda df: prep_grade(df.grade_2),
            difficulty_2=lambda df: df.grade_2.replace(GRADE_DIFFICULTY),
            grade_3=lambda df: prep_grade(df.grade_3),
            difficulty_3=lambda df: df.grade_3.replace(GRADE_DIFFICULTY),
        )

    def grades(self, week: int):
        return self.make_dataframe(f"Week {week} Grades").assign(
            grade=lambda df: prep_grade(df.grade),
            difficulty=lambda df: df.grade.replace(GRADE_DIFFICULTY),
        )

    def scores(self, week: int):
        return scoring.score_climbs(self.climbs(week), self.climbers())

    def old_scores(self, week: int):
        return scoring.score_climbs(self.climbs(week), self.grades(week))

    def print_scores(self, week: int):
        scores = self.scores(week)
        teams = scoring.score_teams(self.teams(), scores)
        scoring.print_night_results(teams, scores)

    def leaderboard(self):
        scoring.print_leader_board(self.teams(), self.climbers())

    def weeks(self):
        return list(
            map(
                lambda x: int(x.split(" ")[1]),
                filter(
                    lambda x: "Climbs" in x,
                    map(lambda x: x.title, self.wks.worksheets()),
                ),
            )
        )

    def season_scores(self):
        return pd.concat(
            [self.old_scores(week).assign(week=week) for week in self.weeks()],
            ignore_index=True,
        )
