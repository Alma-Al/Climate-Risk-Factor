# Research Memo: LLM-Extracted Climate Risk and Asset Returns

## Motivation

Climate risk is increasingly discussed in corporate disclosures, but the text is semi-structured and difficult to summarize with simple keyword counts. I built this project to test whether an LLM-assisted pipeline can turn disclosure language into firm-level risk signals that are auditable enough for empirical asset-pricing work.

## Research Question

Can climate-risk language in corporate disclosures be converted into a firm-level signal, and can that signal be used to construct a climate-risk factor whose returns can be tested against standard asset-pricing controls?

## Current Version

This version proves the end-to-end workflow:

1. Read disclosure text.
2. Extract physical, transition, litigation, and opportunity scores.
3. Preserve evidence sentences and confidence.
4. Build cross-sectional firm-year climate signals.
5. Sort firms into high/low climate-risk portfolios.
6. Construct a high-minus-low climate risk factor.
7. Run summary statistics, factor regressions, and predictive regressions.

The project includes a deterministic rules extractor and an OpenAI-compatible extractor. The rules extractor is deliberately transparent so that failures are inspectable.

## What The Results Mean

The current numerical results should be interpreted as a demonstration of the pipeline, not as an empirical claim about climate risk pricing. The included disclosures are synthetic examples designed to let the repository run without proprietary data or API calls.

The more important output at this stage is the research infrastructure: structured extraction, validation hooks, factor construction, and reproducible analysis artifacts.

## Validation Philosophy

I added a small hand-labeled evaluation set because LLM/NLP projects can otherwise look convincing without being measured. The first validation target is not perfect accuracy. The goal is to catch basic category mistakes:

- Physical vs transition risk confusion
- Treating climate opportunity language as downside risk
- High scores with weak evidence
- Boilerplate mentions receiving too much weight

## Next Step

The project becomes much more compelling once the synthetic disclosures are replaced with real 10-K sections. My next iteration would use a small manually reviewed SEC sample, compare LLM scores against the rules baseline, and test whether industry-neutral climate-risk sorts produce different return patterns.
