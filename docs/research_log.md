# Research Log

This log records the main design choices behind the climate-risk extraction project. 

## 1. Why Start With 10-K-Style Disclosures

I started with 10-K risk-factor / MD&A-style language rather than sustainability reports because sustainability reports often read like marketing documents. Risk factors are more legally constrained and more likely to describe downside exposure. For a first asset-pricing signal, I want text that is closer to what investors might treat as material risk disclosure.

The current repository uses synthetic disclosure excerpts so the pipeline runs anywhere. That means the output tables are workflow demonstrations, not market evidence. The next serious empirical step is replacing the sample excerpts with real SEC filing sections.

## 2. Why Separate Physical, Transition, Litigation, and Opportunity Scores

I do not think a single "climate score" is enough. Physical risk and transition risk are economically different:

- Physical risk is about assets, operations, supply chains, and geography.
- Transition risk is about policy, technology, energy demand, carbon pricing, and changing consumer behavior.
- Litigation risk is a separate channel because legal/disclosure exposure may matter even when operations are not directly climate-sensitive.
- Opportunity language matters because a company can discuss climate heavily due to upside exposure, not just downside risk.

The overall score is therefore a weighted summary, but the sub-scores are preserved for later tests.

## 3. Why Include a Rules Baseline

The rules baseline is not meant to be state of the art. It is there because a portfolio project should not hide all logic behind an LLM call. A transparent baseline makes it possible to inspect obvious false positives and to compare whether LLM extraction is actually adding value beyond a climate dictionary.

This also makes the project easier to run without API keys.

## 4. Why High Climate Risk Minus Low Climate Risk

The first factor is:

```text
High disclosed climate risk portfolio - Low disclosed climate risk portfolio
```

There are two possible interpretations:

- If climate risk is compensated, high-risk firms may earn higher future returns.
- If disclosure captures underpriced operating, regulatory, or litigation exposure, high-risk firms may underperform.

The sign is an empirical question. I do not want the code to imply that "climate risk factor" must always mean a positive return premium.

## 5. Current Weaknesses

- The current sample disclosures are synthetic.
- The labeled evaluation set is small and hand-built for sanity checking, not a substitute for expert annotation.
- The rules extractor can confuse opportunity language with transition exposure when both appear in the same sentence.
- The factor tests do not yet do industry-neutral sorting, which is important because climate risk is sector concentrated.
- The OpenAI extractor path exists, but the repository does not yet include a saved LLM-vs-rules comparison on real filings.

## 6. Next Research Priority

1. Pull a small panel of actual 10-K risk-factor sections from the SEC.
2. Score them with both rules and LLM extractors.
3. Compare against hand labels on 25-50 passages.
4. Run industry-neutral portfolio sorts.