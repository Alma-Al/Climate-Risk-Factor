# LLM Climate Risk Factor Research Pipeline

This project is a prototype research pipeline for extracting climate-risk signals from corporate disclosures and testing whether those signals have asset-pricing relevance.

The included disclosure data is synthetic so the repository can run without paid datasets or API keys.

## What It Does

- Scores disclosure text across physical, transition, litigation, and opportunity channels
- Preserves evidence sentences so extractions can be inspected
- Includes both an OpenAI-compatible extractor and a transparent rules baseline
- Evaluates the extractor against a small hand-labeled sanity-check set
- Constructs high-minus-low climate-risk portfolios
- Runs portfolio summaries, factor regressions, and predictive regressions
- Produces charts, tables, research notes, and validation outputs

## Repo Layout

```text
climate-risk-factor/
  data/
    eval/
    raw/
    processed/
  docs/
    research_log.md
  outputs/
    charts/
    tables/
  prompts/
    climate_risk_prompt.md
  reports/
    research_memo.md
  scripts/
    00_make_sample_data.py
    01_extract_climate_signals.py
    02_build_factor.py
    03_run_asset_pricing_tests.py
    04_analyze_outputs.py
    06_evaluate_extractor.py
    run_pipeline.py
  src/climate_risk_factor/
    factor_model.py
    llm_extractor.py
    plots.py
    signal_builder.py
  tests/
  requirements.txt
```

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/06_evaluate_extractor.py
python scripts/07_run_tests.py
```

The pipeline writes:

- `data/processed/climate_scores.csv`
- `data/processed/monthly_factor_returns.csv`
- `outputs/tables/portfolio_summary.csv`
- `outputs/tables/factor_regressions.csv`
- `outputs/tables/predictive_regression.csv`
- `outputs/tables/extractor_eval.csv`
- `outputs/charts/cumulative_factor_returns.png`
- `outputs/charts/risk_score_distribution.png`

## What Is Real vs. Demonstration

The code path is real: extraction, scoring, factor construction, and regression testing all run end to end.

The current sample disclosures are synthetic. The generated asset-pricing results should therefore be read as a demonstration, not as evidence that climate risk is or is not priced.

## Using a Real LLM

By default, the extractor uses a transparent keyword/rule fallback so the project runs without API keys.

To use OpenAI-compatible structured extraction:

```bash
export OPENAI_API_KEY="your_key"
python scripts/01_extract_climate_signals.py --provider openai
```

The LLM prompt is in `prompts/climate_risk_prompt.md`.

## Development Approach

This project was built using an LLM-assisted workflow. I used Codex to help scaffold and iterate on parts of the codebase, but I designed the core research pipeline myself, including:

- defining the climate-risk taxonomy (transition, physical, regulatory, opportunity)
- constructing the firm-year signal and composite score
- ensuring no look-ahead bias by matching signals from year t to returns in year t+1
- building the high-minus-low factor construction
- implementing regression and evaluation logic

I also included a rules-based baseline and simple validation checks to compare against LLM outputs, since model-generated scores can be inconsistent or sensitive to phrasing.

## Extractor Evaluation

The repository includes a small hand-labeled evaluation set:

```text
data/eval/labeled_disclosures.csv
```

Run:

```bash
python scripts/06_evaluate_extractor.py
```

The evaluator reports:

- mean absolute error
- exact match rate
- within-one accuracy
- mean signed error

This is not a substitute for expert annotation, but it catches basic failures such as confusing opportunity language with downside risk or over-scoring boilerplate climate mentions.

## Research Framing

The main test is whether a portfolio long high-climate-risk firms and short low-climate-risk firms earns returns not explained by broad market and style factors.

Core factor definition:

```text
Climate Risk Factor_t = Return(High Climate Risk Portfolio)_t - Return(Low Climate Risk Portfolio)_t
```

The project also estimates a predictive regression:

```text
forward_return_i,t = alpha + beta * climate_risk_score_i,t + controls + error_i,t
```

