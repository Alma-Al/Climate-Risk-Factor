from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MPL_CACHE = ROOT / ".cache" / "matplotlib"
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
except ImportError:  # pragma: no cover
    sns = None


def plot_cumulative_factor_returns(factor_returns: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = factor_returns.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["cumulative_high"] = (1 + frame["high"].fillna(0)).cumprod() - 1
    frame["cumulative_low"] = (1 + frame["low"].fillna(0)).cumprod() - 1
    frame["cumulative_factor"] = (1 + frame["climate_risk_factor"].fillna(0)).cumprod() - 1

    plt.figure(figsize=(10, 6))
    plt.plot(frame["date"], frame["cumulative_high"], label="High climate risk")
    plt.plot(frame["date"], frame["cumulative_low"], label="Low climate risk")
    plt.plot(frame["date"], frame["cumulative_factor"], label="High - Low", linewidth=2.4)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Cumulative Climate Risk Portfolio Returns")
    plt.ylabel("Cumulative return")
    plt.xlabel("Date")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_score_distribution(scores: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 5))
    if sns is not None:
        sns.histplot(
            data=scores,
            x="overall_climate_risk_score",
            hue="filing_year",
            multiple="stack",
            bins=10,
        )
    else:
        plt.hist(scores["overall_climate_risk_score"], bins=10)
    plt.title("Distribution of Climate Risk Scores")
    plt.xlabel("Overall climate risk score")
    plt.ylabel("Firm-years")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
