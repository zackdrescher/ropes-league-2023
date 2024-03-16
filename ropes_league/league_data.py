from abc import ABC, abstractmethod
import os

from dotenv import load_dotenv
import gspread
import pandas as pd


load_dotenv()

gc = gspread.service_account(
    scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
)


def prep_grade(grade):
    return grade.replace({5.1: "5.10", "No Climb": "X"}).astype(str)


def make_dataframe(records, index=None):
    return pd.DataFrame.from_records(records, index=index)


def climb_string(row):
    l1 = "L" if row.rope_1 == "Lead" else ""
    l2 = "L" if row.rope_2 == "Lead" else ""
    l3 = "L" if row.rope_3 == "Lead" else ""
    return f"{row.grade_1}{l1} {row.grade_2}{l2} {row.grade_3}{l3}"


class LeagueData(ABC):
    @classmethod
    def from_env(cls):
        return cls.from_key(os.getenv("LEAGUE_SHEET_KEY"))

    @classmethod
    def from_key(cls, key: str):
        return cls(gc.open_by_key(key))

    def __init__(self, wks) -> None:
        self.wks = wks

    def make_dataframe(self, sheet: str, index=None):
        return make_dataframe(self.wks.worksheet(sheet).get_all_records(), index=index)

    @abstractmethod
    def climbers(self):
        pass

    @abstractmethod
    def climbs(self, week: int):
        pass

    @abstractmethod
    def scores(self, week: int):
        pass
