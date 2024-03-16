import pandas as pd

from ..league_data import LeagueData, prep_grade


GRADE_SCORE = {
    "X": 0,
    "5.7": 1,
    "5.8": 2,
    "5.9": 3,
    "5.10-": 4,
    "5.10": 5,
    "5.10+": 6,
    "5.11-": 7,
    "5.11": 8,
    "5.11+": 9,
    "5.12-": 10,
    "5.12": 11,
    "5.12+": 12,
    "5.13-": 13,
    "5.13": 14,
    "5.13+": 15,
}


def format_change(change: int):
    if change == 0:
        return "-"
    elif change > 0:
        return f"+{change}"
    else:
        return str(change)


class IndividualLeagueData(LeagueData):
    def climbers(self):
        return (
            self.make_dataframe("Climbers")
            .assign(email=lambda df: df.email.str.lower().str.strip())
            .query('paid == "TRUE"')
        )

    def climbs(self, week: int):
        return self.make_dataframe(f"Session {week}").assign(
            email=lambda df: df.email.str.lower().str.strip(),
            grade_1=lambda df: prep_grade(df.grade_1),
            grade_2=lambda df: prep_grade(df.grade_2),
            grade_3=lambda df: prep_grade(df.grade_3),
        )

    def scores(self, week: int):
        return (
            self.climbers()[["name", "email"]]
            .merge(
                self.climbs(week)
                .assign(
                    score_1=lambda df: df.grade_1.replace(GRADE_SCORE)
                    + ((df.rope_1 == "Lead") * 1),
                    score_2=lambda df: df.grade_2.replace(GRADE_SCORE)
                    + ((df.rope_2 == "Lead") * 1),
                    score_3=lambda df: df.grade_3.replace(GRADE_SCORE)
                    + ((df.rope_3 == "Lead") * 1),
                    score=lambda df: df[["score_1", "score_2", "score_3"]].sum(axis=1),
                )
                .drop(["timestamp", "name", "score_1", "score_2", "score_3"], axis=1),
                how="inner",
                on="email",
            )
            .sort_values("score", ascending=False)
        )

    def results(self, week: int):
        def grade_string_lambda(grade_col, rope_col):
            return lambda df: df[grade_col] + df[rope_col].map(
                {"Lead": "L", "Top Rope": ""}
            )

        scores = self.scores(week)

        return (
            scores.assign(
                climb_1=grade_string_lambda("grade_1", "rope_1"),
                climb_2=grade_string_lambda("grade_2", "rope_2"),
                climb_3=grade_string_lambda("grade_3", "rope_3"),
            )
            .drop(
                columns=[
                    "grade_1",
                    "rope_1",
                    "grade_2",
                    "rope_2",
                    "grade_3",
                    "rope_3",
                ],
            )
            .set_index(pd.Index(range(1, len(scores) + 1)))
        )

    def standings(self, week: int):
        results = self.results(week)
        if week == 1:
            return results.drop(["climb_1", "climb_2", "climb_3"], axis=1).assign(
                points_earned=lambda df: df.score, change=0
            )
        else:

            standings = (
                pd.concat([self.scores(i) for i in range(1, week)])
                .groupby("email")
                .score.sum()
                .sort_values(ascending=False)
                .reset_index()
                .reset_index(names="prior_rank")
                .merge(
                    results[["email", "score"]].rename(
                        columns={"score": "points_earned"}
                    ),
                    how="left",
                    on="email",
                )
                .assign(
                    points_earned=lambda df: df.points_earned.fillna(0),
                    score=lambda df: df.points_earned + df.score,
                )
                .sort_values("score", ascending=False)
                .reset_index(drop=True)
                .assign(
                    change=lambda df: (df.prior_rank - df.index).apply(format_change)
                )
                .drop(columns="prior_rank")
                .merge(self.climbers()[["email", "name"]], how="left", on="email")
            )

            standings.index += 1

            return standings

    def sessions(self):
        return list(
            map(
                lambda x: int(x.split(" ")[1]),
                filter(
                    lambda x: "Session" in x,
                    map(lambda x: x.title, self.wks.worksheets()),
                ),
            )
        )
