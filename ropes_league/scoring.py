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
