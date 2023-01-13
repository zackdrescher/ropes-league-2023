import pandas as pd
import numpy as np


def points(threshold, climb, type):
    return (climb - threshold + 1 + np.where(type == "Lead", 0.5, 0)).fillna(0)


def score_climbs(climbs: pd.DataFrame, climbers: pd.DataFrame) -> pd.DateOffset:
    return climbs.merge(
        climbers[["name", "difficulty"]].rename(
            columns={"difficulty": "climber_difficulty"}
        ),
        left_on="climber_id",
        right_index=True,
    ).assign(
        points_1=lambda df: points(df.climber_difficulty, df.difficulty_1, df.rope_1),
        points_2=lambda df: points(df.climber_difficulty, df.difficulty_2, df.rope_2),
        points_3=lambda df: points(df.climber_difficulty, df.difficulty_3, df.rope_3),
        points=lambda df: df[["points_1", "points_2", "points_3"]].sum(axis=1),
    )


def score_teams(teams: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    return (
        teams.assign(scores=scores.groupby("team_id").points.sum())
        .sort_values("scores", ascending=False)
        .assign(
            points_earned=np.arange(1, len(teams) + 1)[::-1],
            points=lambda df: df.points_earned + df.points,
        )
    )


def climb_string(row):
    l1 = "L" if row.rope_1 == "Lead" else ""
    l2 = "L" if row.rope_2 == "Lead" else ""
    l3 = "L" if row.rope_3 == "Lead" else ""
    return f"{row.grade_1}{l1} {row.grade_2}{l2} {row.grade_3}{l3}"


def print_night_results(teams: pd.DataFrame, scores: pd.DataFrame):
    for i, (team, t) in enumerate(teams.sort_values("scores").iterrows()):
        c = scores[scores.team_id == team]
        print(f"{i + 1}. {t['name']} {t.emoji} - {t.scores} points")

        for i, row in c.sort_values("points", ascending=False).iterrows():
            print(f"    {row['name']} - {climb_string(row)} - {row.points}")


def print_leader_board(teams: pd.DataFrame, climbers: pd.DataFrame):
    for i, (team, t) in enumerate(
        teams.sort_values("points", ascending=False).iterrows()
    ):
        print(f"{i + 1}. {t['name']} {t.emoji} - {t.points} points")
        c = climbers[climbers.team == team]
        for i, row in c.sort_values("difficulty", ascending=False).iterrows():
            print(f"    {row['name']} - {row.grade}")
