from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import _path  # noqa: F401
from climate_risk_factor.llm_extractor import score_disclosure


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = {
    "physical_risk_score": "expected_physical",
    "transition_risk_score": "expected_transition",
    "litigation_risk_score": "expected_litigation",
    "opportunity_score": "expected_opportunity",
}


def evaluate(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for predicted_col, expected_col in EXPECTED_COLUMNS.items():
        errors = predictions[predicted_col] - predictions[expected_col]
        rows.append(
            {
                "score_type": predicted_col.replace("_risk_score", "").replace("_score", ""),
                "mean_absolute_error": errors.abs().mean(),
                "exact_match_rate": (errors == 0).mean(),
                "within_one_rate": (errors.abs() <= 1).mean(),
                "mean_signed_error": errors.mean(),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=ROOT / "data/eval/labeled_disclosures.csv")
    parser.add_argument("--output", default=ROOT / "outputs/tables/extractor_eval.csv")
    parser.add_argument("--predictions-output", default=ROOT / "outputs/tables/extractor_eval_predictions.csv")
    parser.add_argument("--provider", choices=["rules", "openai"], default="rules")
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--prompt", default=ROOT / "prompts/climate_risk_prompt.md")
    args = parser.parse_args()

    labeled = pd.read_csv(args.input)
    prediction_rows = []
    for row in labeled.to_dict("records"):
        score = score_disclosure(
            ticker=row["ticker"],
            company=row["company"],
            filing_year=int(row["filing_year"]),
            text=row["disclosure_text"],
            provider=args.provider,
            prompt_path=args.prompt,
            model=args.model,
        ).to_dict()
        prediction_rows.append({**row, **score})

    predictions = pd.DataFrame(prediction_rows)
    metrics = evaluate(predictions)

    output = Path(args.output)
    predictions_output = Path(args.predictions_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    predictions_output.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output, index=False)
    predictions.to_csv(predictions_output, index=False)

    print("\nExtractor evaluation")
    print("====================")
    print(metrics.round(3).to_string(index=False))
    print(f"\nWrote metrics to {output}")
    print(f"Wrote predictions to {predictions_output}")


if __name__ == "__main__":
    main()
