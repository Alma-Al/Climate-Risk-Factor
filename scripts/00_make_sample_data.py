from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


COMPANIES = [
    ("XOM", "Exxon Mobil", "energy", 4.6),
    ("NEE", "NextEra Energy", "utilities", 2.2),
    ("AAPL", "Apple", "technology", 1.3),
    ("MSFT", "Microsoft", "technology", 1.1),
    ("TSLA", "Tesla", "automobiles", 2.0),
    ("DAL", "Delta Air Lines", "airlines", 3.2),
    ("WMT", "Walmart", "retail", 1.8),
    ("DUK", "Duke Energy", "utilities", 3.5),
    ("CAT", "Caterpillar", "industrials", 2.8),
    ("JPM", "JPMorgan Chase", "financials", 1.9),
]


DISCLOSURE_TEMPLATES = {
    "energy": (
        "Climate change regulation, carbon price mechanisms, greenhouse gas emissions "
        "standards, and the energy transition could materially affect demand for our "
        "products and capital expenditure plans. Severe storms, hurricanes, flooding, "
        "and other extreme weather may disrupt refineries, pipelines, and supply chain "
        "operations. Environmental litigation and compliance proceedings may also "
        "adversely affect operating results."
    ),
    "utilities": (
        "Our operations face physical risk from hurricanes, wildfire, heat, drought, "
        "and water scarcity. Emissions regulation, renewable portfolio standards, "
        "decarbonization requirements, and coal plant retirement could require "
        "significant capital expenditure. We also see opportunity in renewable energy, "
        "energy efficiency, and low-carbon grid investment."
    ),
    "technology": (
        "Climate-related matters may affect facilities, suppliers, and electricity "
        "procurement. Extreme weather could disrupt logistics or data center operations, "
        "but we do not expect a material adverse effect. We continue to purchase "
        "renewable energy and improve energy efficiency across operations."
    ),
    "automobiles": (
        "Fuel economy rules, emissions regulation, electrification, and changing "
        "consumer preferences are significant to our business model. Demand for electric "
        "vehicle products creates low-carbon opportunity, while battery supply chains "
        "may face climate-related disruption and compliance risk."
    ),
    "airlines": (
        "Carbon tax proposals, sustainable aviation fuel mandates, greenhouse gas "
        "emissions regulation, and energy transition policies could materially increase "
        "operating costs. Hurricanes, storms, heat, and extreme weather may disrupt "
        "flight operations. Climate litigation and environmental claims remain possible."
    ),
    "retail": (
        "Extreme weather, hurricanes, flooding, drought, and heat may disrupt stores, "
        "distribution centers, and suppliers. We monitor greenhouse gas emissions, "
        "renewable energy procurement, and energy efficiency initiatives, though climate "
        "risks are one of many operating risks."
    ),
    "industrials": (
        "Emissions regulation, carbon price policies, decarbonization, and changing "
        "customer demand may affect heavy equipment markets. Physical risk from storms, "
        "flooding, and supply chain disruption could affect production. Clean technology "
        "and energy efficiency investments may create opportunity."
    ),
    "financials": (
        "Climate-related disclosure, litigation, and compliance expectations may affect "
        "risk management. Borrowers may be exposed to flood, wildfire, drought, carbon "
        "price policies, and transition risk. We are developing sustainable product and "
        "green infrastructure financing capabilities."
    ),
}


def make_disclosures(years: range) -> pd.DataFrame:
    rows = []
    for year in years:
        for ticker, company, industry, _risk in COMPANIES:
            year_phrase = (
                " The potential impact has become more significant this year."
                if year >= 2023 and industry in {"energy", "airlines", "utilities"}
                else " Management continues to evaluate these risks."
            )
            rows.append(
                {
                    "ticker": ticker,
                    "company": company,
                    "industry": industry,
                    "filing_year": year,
                    "disclosure_text": DISCLOSURE_TEMPLATES[industry] + year_phrase,
                }
            )
    return pd.DataFrame(rows)


def make_returns(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(42)
    dates = pd.date_range(start=start, end=end, freq="ME")

    factor_rows = []
    return_rows = []
    company_meta = {ticker: (industry, risk) for ticker, _company, industry, risk in COMPANIES}
    industry_beta = {
        "energy": 1.10,
        "utilities": 0.70,
        "technology": 1.20,
        "automobiles": 1.35,
        "airlines": 1.45,
        "retail": 0.90,
        "industrials": 1.05,
        "financials": 1.00,
    }

    momentum_state = {ticker: 0.0 for ticker, *_ in COMPANIES}
    for date in dates:
        mkt_rf = rng.normal(0.006, 0.042)
        smb = rng.normal(0.001, 0.025)
        hml = rng.normal(0.001, 0.027)
        rmw = rng.normal(0.001, 0.018)
        cma = rng.normal(0.001, 0.018)
        mom = rng.normal(0.002, 0.03)
        rf = 0.0025
        factor_rows.append(
            {
                "date": date,
                "mkt_rf": mkt_rf,
                "smb": smb,
                "hml": hml,
                "rmw": rmw,
                "cma": cma,
                "mom": mom,
                "rf": rf,
            }
        )

        climate_shock = rng.normal(0.0015, 0.015)
        for ticker, company, industry, risk in COMPANIES:
            beta = industry_beta[industry]
            size_tilt = -0.001 if industry in {"technology", "financials"} else 0.001
            climate_loading = (risk - 2.4) * climate_shock
            idio = rng.normal(0.0, 0.055)
            ret = rf + beta * mkt_rf + size_tilt * smb + 0.20 * hml + climate_loading + idio
            market_cap = float(rng.lognormal(mean=11.2 - 0.10 * risk, sigma=0.35))
            momentum_state[ticker] = 0.85 * momentum_state[ticker] + ret
            return_rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "company": company,
                    "industry": industry,
                    "ret": ret,
                    "market_cap": market_cap,
                    "log_market_cap": np.log(market_cap),
                    "momentum_12_1": momentum_state[ticker],
                }
            )

    return pd.DataFrame(return_rows), pd.DataFrame(factor_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=ROOT / "data")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    disclosures = make_disclosures(range(2021, 2025))
    returns, factors = make_returns("2022-01-31", "2025-12-31")

    disclosures.to_csv(raw_dir / "sample_disclosures.csv", index=False)
    returns.to_csv(raw_dir / "sample_monthly_returns.csv", index=False)
    factors.to_csv(raw_dir / "sample_benchmark_factors.csv", index=False)

    print(f"Wrote {len(disclosures)} disclosure rows to {raw_dir / 'sample_disclosures.csv'}")
    print(f"Wrote {len(returns)} return rows to {raw_dir / 'sample_monthly_returns.csv'}")
    print(f"Wrote {len(factors)} factor rows to {raw_dir / 'sample_benchmark_factors.csv'}")


if __name__ == "__main__":
    main()
