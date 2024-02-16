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


def make_dataframe(records, index=None):
    return pd.DataFrame.from_records(records, index=index)


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
