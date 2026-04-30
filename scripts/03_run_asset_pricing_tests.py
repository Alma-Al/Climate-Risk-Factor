from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import _path  # noqa: F401
from climate_risk_factor.factor_model import run_factor_regression, run_predictive_regression


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default=ROOT / "data/processed/climate_scores.csv")
    parser.add_argument("--returns", default=ROOT / "data/raw/sample_monthly_returns.csv")
    parser.add_argument("--factor-returns", default=ROOT / "data/processed/monthly_factor_returns.csv")
    parser.add_argument("--benchmark-factors", default=ROOT / "data/raw/sample_benchmark_factors.csv")
    parser.add_argument("--factor-reg-output", default=ROOT / "outputs/tables/factor_regressions.csv")
    parser.add_argument("--predictive-reg-output", default=ROOT / "outputs/tables/predictive_regression.csv")
    args = parser.parse_args()

    scores = pd.read_csv(args.scores)
    returns = pd.read_csv(args.returns)
    factor_returns = pd.read_csv(args.factor_returns)
    benchmark_factors = pd.read_csv(args.benchmark_factors)

    factor_reg = run_factor_regression(factor_returns, benchmark_factors)
    predictive_reg = run_predictive_regression(returns, scores)

    factor_output = Path(args.factor_reg_output)
    predictive_output = Path(args.predictive_reg_output)
    factor_output.parent.mkdir(parents=True, exist_ok=True)
    predictive_output.parent.mkdir(parents=True, exist_ok=True)

    factor_reg.to_csv(factor_output, index=False)
    predictive_reg.to_csv(predictive_output, index=False)

    print(f"Wrote factor regression to {factor_output}")
    print(f"Wrote predictive regression to {predictive_output}")


if __name__ == "__main__":
    main()
