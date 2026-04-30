from __future__ import annotations

import pandas as pd


def add_signal_columns(scores: pd.DataFrame) -> pd.DataFrame:
    frame = scores.copy()
    frame["risk_minus_opportunity"] = (
        frame["overall_climate_risk_score"] - 0.35 * frame["opportunity_score"]
    )
    frame["transition_minus_physical"] = (
        frame["transition_risk_score"] - frame["physical_risk_score"]
    )
    frame["climate_risk_z"] = frame.groupby("filing_year")[
        "overall_climate_risk_score"
    ].transform(lambda s: (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) else 0.0)
    frame["risk_rank"] = frame.groupby("filing_year")[
        "overall_climate_risk_score"
    ].rank(pct=True)
    return frame


def assign_portfolios(
    scores: pd.DataFrame,
    quantile: float = 0.3,
    score_col: str = "overall_climate_risk_score",
) -> pd.DataFrame:
    if not 0 < quantile < 0.5:
        raise ValueError("quantile must be between 0 and 0.5.")

    frame = scores.copy()

    def _assign(group: pd.DataFrame) -> pd.Series:
        low_cut = group[score_col].quantile(quantile)
        high_cut = group[score_col].quantile(1 - quantile)
        labels = pd.Series("middle", index=group.index)
        labels[group[score_col] <= low_cut] = "low"
        labels[group[score_col] >= high_cut] = "high"
        return labels

    labels = []
    for _year, group in frame.groupby("filing_year"):
        labels.append(_assign(group))
    frame["climate_portfolio"] = pd.concat(labels).sort_index()
    return frame


def prepare_signal_table(scores: pd.DataFrame, quantile: float = 0.3) -> pd.DataFrame:
    return assign_portfolios(add_signal_columns(scores), quantile=quantile)
