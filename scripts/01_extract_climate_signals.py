from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import _path  # noqa: F401
from climate_risk_factor.llm_extractor import score_disclosure
from climate_risk_factor.signal_builder import prepare_signal_table


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=ROOT / "data/raw/sample_disclosures.csv")
    parser.add_argument("--output", default=ROOT / "data/processed/climate_scores.csv")
    parser.add_argument("--provider", choices=["rules", "openai"], default="rules")
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--portfolio-quantile", type=float, default=0.3)
    parser.add_argument("--prompt", default=ROOT / "prompts/climate_risk_prompt.md")
    args = parser.parse_args()

    disclosures = pd.read_csv(args.input)
    rows = []
    for row in tqdm(disclosures.to_dict("records"), desc="Scoring disclosures"):
        score = score_disclosure(
            ticker=row["ticker"],
            company=row["company"],
            filing_year=int(row["filing_year"]),
            text=row["disclosure_text"],
            provider=args.provider,
            prompt_path=args.prompt,
            model=args.model,
        )
        scored = score.to_dict()
        scored["industry"] = row.get("industry")
        rows.append(scored)

    scores = pd.DataFrame(rows)
    scores = prepare_signal_table(scores, quantile=args.portfolio_quantile)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    scores.to_csv(output, index=False)
    print(f"Wrote climate scores to {output}")


if __name__ == "__main__":
    main()
