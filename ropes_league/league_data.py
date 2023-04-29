import os

from dotenv import load_dotenv
import gspread
import numpy as np
import pandas as pd

from . import scoring

load_dotenv()

gc = gspread.service_account(
    scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
)

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


def make_dataframe(records, index=None):
    return pd.DataFrame.from_records(records, index=index)


def prep_grade(grade):
    return grade.replace({5.1: "5.10", "No Climb": "X"}).astype(str)


class LeagueData:
    @classmethod
    def from_env(cls):
        return cls.from_key(os.getenv("LEAGUE_SHEET_KEY"))

    @classmethod
    def from_key(cls, key: str):
        return cls(gc.open_by_key(key))

    def __init__(self, wks) -> None:
        self.wks = wks

    def climbers(self):
        return make_dataframe(
            self.wks.worksheet("Climbers").get_all_records(), "id"
        ).assign(
            grade=lambda df: prep_grade(df.grade),
            difficulty=lambda df: df.grade.replace(GRADE_DIFFICULTY),
        )

    def teams(self):
        return make_dataframe(self.wks.worksheet("Teams").get_all_records(), "id")

    def climbs(self, week: int):
        return make_dataframe(
            self.wks.worksheet(f"Week {week} Climbs").get_all_records()
        ).assign(
            grade_1=lambda df: prep_grade(df.grade_1),
            difficulty_1=lambda df: df.grade_1.replace(GRADE_DIFFICULTY),
            grade_2=lambda df: prep_grade(df.grade_2),
            difficulty_2=lambda df: df.grade_2.replace(GRADE_DIFFICULTY),
            grade_3=lambda df: prep_grade(df.grade_3),
            difficulty_3=lambda df: df.grade_3.replace(GRADE_DIFFICULTY),
        )

    def grades(self, week: int):
        return make_dataframe(
            self.wks.worksheet(f"Week {week} Grades").get_all_records()
        ).assign(
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
