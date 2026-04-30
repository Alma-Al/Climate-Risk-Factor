from __future__ import annotations

import pandas as pd

from climate_risk_factor.factor_model import construct_factor_returns, summarize_returns


def test_construct_factor_returns_uses_prior_year_signal() -> None:
    signals = pd.DataFrame(
        {
            "ticker": ["A", "B"],
            "filing_year": [2022, 2022],
            "overall_climate_risk_score": [5.0, 0.5],
            "climate_portfolio": ["high", "low"],
        }
    )
    returns = pd.DataFrame(
        {
            "date": ["2023-01-31", "2023-01-31", "2023-02-28", "2023-02-28"],
            "ticker": ["A", "B", "A", "B"],
            "ret": [0.04, 0.01, -0.02, 0.01],
        }
    )

    factor_returns = construct_factor_returns(returns, signals)

    assert list(factor_returns["climate_risk_factor"].round(4)) == [0.03, -0.03]
    summary = summarize_returns(factor_returns)
    assert "climate_risk_factor" in set(summary["portfolio"])
