from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import _path  # noqa: F401
from climate_risk_factor.plots import plot_cumulative_factor_returns, plot_score_distribution


ROOT = Path(__file__).resolve().parents[1]


def print_table(title: str, frame: pd.DataFrame) -> None:
    print(f"\n{title}")
    print("=" * len(title))
    print(frame.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default=ROOT / "data/processed/climate_scores.csv")
    parser.add_argument("--factor-returns", default=ROOT / "data/processed/monthly_factor_returns.csv")
    parser.add_argument("--summary", default=ROOT / "outputs/tables/portfolio_summary.csv")
    parser.add_argument("--factor-reg", default=ROOT / "outputs/tables/factor_regressions.csv")
    parser.add_argument("--predictive-reg", default=ROOT / "outputs/tables/predictive_regression.csv")
    parser.add_argument("--charts-dir", default=ROOT / "outputs/charts")
    args = parser.parse_args()

    scores = pd.read_csv(args.scores)
    factor_returns = pd.read_csv(args.factor_returns)
    summary = pd.read_csv(args.summary)
    factor_reg = pd.read_csv(args.factor_reg)
    predictive_reg = pd.read_csv(args.predictive_reg)

    charts_dir = Path(args.charts_dir)
    plot_cumulative_factor_returns(factor_returns, charts_dir / "cumulative_factor_returns.png")
    plot_score_distribution(scores, charts_dir / "risk_score_distribution.png")

    top_scores = scores.sort_values("overall_climate_risk_score", ascending=False).head(8)
    print_table(
        "Highest Climate Risk Firm-Years",
        top_scores[
            [
                "ticker",
                "filing_year",
                "industry",
                "overall_climate_risk_score",
                "physical_risk_score",
                "transition_risk_score",
                "opportunity_score",
                "climate_portfolio",
            ]
        ],
    )
    print_table("Portfolio Summary", summary.round(4))
    print_table("Factor Regression", factor_reg.round(4))
    print_table("Predictive Regression", predictive_reg.round(4))
    print(f"\nCharts written to {charts_dir}")


if __name__ == "__main__":
    main()
