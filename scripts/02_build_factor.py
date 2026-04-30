from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import _path  # noqa: F401
from climate_risk_factor.factor_model import construct_factor_returns, summarize_returns


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default=ROOT / "data/processed/climate_scores.csv")
    parser.add_argument("--returns", default=ROOT / "data/raw/sample_monthly_returns.csv")
    parser.add_argument("--factor-output", default=ROOT / "data/processed/monthly_factor_returns.csv")
    parser.add_argument("--summary-output", default=ROOT / "outputs/tables/portfolio_summary.csv")
    parser.add_argument("--value-weighted", action="store_true")
    args = parser.parse_args()

    scores = pd.read_csv(args.scores)
    returns = pd.read_csv(args.returns)
    factor_returns = construct_factor_returns(
        returns=returns,
        signal_table=scores,
        value_weighted=args.value_weighted,
    )
    summary = summarize_returns(factor_returns)

    factor_output = Path(args.factor_output)
    summary_output = Path(args.summary_output)
    factor_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.parent.mkdir(parents=True, exist_ok=True)

    factor_returns.to_csv(factor_output, index=False)
    summary.to_csv(summary_output, index=False)

    print(f"Wrote monthly factor returns to {factor_output}")
    print(f"Wrote portfolio summary to {summary_output}")


if __name__ == "__main__":
    main()
