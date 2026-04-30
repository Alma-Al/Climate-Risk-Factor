from __future__ import annotations

import pandas as pd

from climate_risk_factor.signal_builder import prepare_signal_table


def test_prepare_signal_table_assigns_high_and_low_portfolios() -> None:
    scores = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D", "E"],
            "filing_year": [2023] * 5,
            "overall_climate_risk_score": [0.5, 1.0, 2.0, 4.0, 5.0],
            "opportunity_score": [0, 1, 1, 0, 0],
            "transition_risk_score": [0, 1, 2, 4, 5],
            "physical_risk_score": [0, 1, 1, 3, 4],
        }
    )

    prepared = prepare_signal_table(scores, quantile=0.2)

    low = prepared.loc[prepared["ticker"] == "A", "climate_portfolio"].item()
    high = prepared.loc[prepared["ticker"] == "E", "climate_portfolio"].item()
    assert low == "low"
    assert high == "high"
    assert "climate_risk_z" in prepared.columns
