from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class ClimateScore:
    ticker: str
    company: str
    filing_year: int
    physical_risk_score: int
    transition_risk_score: int
    litigation_risk_score: int
    opportunity_score: int
    overall_climate_risk_score: float
    confidence: float
    evidence: list[str]
    provider: str

    def to_dict(self) -> dict:
        row = asdict(self)
        row["evidence"] = json.dumps(self.evidence)
        return row


PHYSICAL_TERMS = {
    "hurricane": 1.1,
    "storm": 0.8,
    "flood": 1.0,
    "wildfire": 1.2,
    "drought": 1.0,
    "water scarcity": 1.2,
    "heat": 0.7,
    "extreme weather": 1.3,
    "sea level": 1.1,
    "physical risk": 1.2,
    "supply chain disruption": 0.8,
}

TRANSITION_TERMS = {
    "carbon price": 1.3,
    "carbon tax": 1.4,
    "emissions regulation": 1.3,
    "greenhouse gas": 0.8,
    "energy transition": 1.3,
    "stranded asset": 1.4,
    "renewable": 0.5,
    "electrification": 0.8,
    "net zero": 0.8,
    "fuel economy": 0.9,
    "transition risk": 1.4,
    "decarbonization": 1.1,
}

LITIGATION_TERMS = {
    "litigation": 1.3,
    "lawsuit": 1.4,
    "legal proceeding": 1.1,
    "environmental claim": 1.2,
    "compliance": 0.6,
    "penalty": 0.8,
    "disclosure": 0.4,
}

OPPORTUNITY_TERMS = {
    "renewable energy": 1.3,
    "clean technology": 1.3,
    "climate adaptation": 1.2,
    "energy efficiency": 1.0,
    "green infrastructure": 1.2,
    "low-carbon": 1.1,
    "electric vehicle": 1.2,
    "sustainable product": 0.9,
}

MATERIALITY_TERMS = {
    "material": 0.8,
    "significant": 0.6,
    "adverse": 0.5,
    "substantial": 0.7,
    "business model": 0.8,
    "capital expenditure": 0.6,
    "operating results": 0.6,
}


def load_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _score_terms(text: str, terms: dict[str, float]) -> tuple[int, list[str]]:
    normalized = _normalize(text)
    raw = 0.0
    evidence = []
    for term, weight in terms.items():
        count = normalized.count(term)
        if count:
            raw += min(count, 3) * weight
            evidence.append(term)

    materiality = sum(weight for term, weight in MATERIALITY_TERMS.items() if term in normalized)
    adjusted = raw * (1.0 + min(materiality, 2.0) * 0.15)

    if adjusted == 0:
        return 0, evidence
    if adjusted < 1.0:
        return 1, evidence
    if adjusted < 2.2:
        return 2, evidence
    if adjusted < 3.8:
        return 3, evidence
    if adjusted < 5.5:
        return 4, evidence
    return 5, evidence


def _extract_evidence(text: str, terms: Iterable[str], limit: int = 3) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    matches = []
    lowered_terms = [term.lower() for term in terms]
    for sentence in sentences:
        sentence_l = sentence.lower()
        if any(term in sentence_l for term in lowered_terms):
            matches.append(sentence.strip())
        if len(matches) >= limit:
            break
    return matches


def score_with_rules(ticker: str, company: str, filing_year: int, text: str) -> ClimateScore:
    physical, physical_hits = _score_terms(text, PHYSICAL_TERMS)
    transition, transition_hits = _score_terms(text, TRANSITION_TERMS)
    litigation, litigation_hits = _score_terms(text, LITIGATION_TERMS)
    opportunity, opportunity_hits = _score_terms(text, OPPORTUNITY_TERMS)

    overall = (
        0.40 * physical
        + 0.45 * transition
        + 0.15 * litigation
        - 0.10 * opportunity
    )
    overall = float(max(0.0, min(5.0, round(overall, 2))))

    hits = physical_hits + transition_hits + litigation_hits + opportunity_hits
    evidence = _extract_evidence(text, hits) if hits else []
    confidence = min(0.95, 0.45 + 0.08 * len(set(hits)))

    return ClimateScore(
        ticker=ticker,
        company=company,
        filing_year=int(filing_year),
        physical_risk_score=physical,
        transition_risk_score=transition,
        litigation_risk_score=litigation,
        opportunity_score=opportunity,
        overall_climate_risk_score=overall,
        confidence=round(confidence, 2),
        evidence=evidence,
        provider="rules",
    )


def _coerce_llm_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content)
        content = re.sub(r"```$", "", content).strip()
    return json.loads(content)


def score_with_openai(
    ticker: str,
    company: str,
    filing_year: int,
    text: str,
    prompt: str,
    model: str = "gpt-4.1-mini",
) -> ClimateScore:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the openai package or use --provider rules.") from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Use --provider rules or export a key.")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    f"Ticker: {ticker}\nCompany: {company}\n"
                    f"Filing year: {filing_year}\n\nDisclosure text:\n{text}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    parsed = _coerce_llm_json(content)

    return ClimateScore(
        ticker=ticker,
        company=company,
        filing_year=int(filing_year),
        physical_risk_score=int(parsed["physical_risk_score"]),
        transition_risk_score=int(parsed["transition_risk_score"]),
        litigation_risk_score=int(parsed["litigation_risk_score"]),
        opportunity_score=int(parsed["opportunity_score"]),
        overall_climate_risk_score=float(parsed["overall_climate_risk_score"]),
        confidence=float(parsed.get("confidence", 0.75)),
        evidence=list(parsed.get("evidence", [])),
        provider="openai",
    )


def score_disclosure(
    ticker: str,
    company: str,
    filing_year: int,
    text: str,
    provider: str = "rules",
    prompt_path: str | Path | None = None,
    model: str = "gpt-4.1-mini",
) -> ClimateScore:
    if provider == "rules":
        return score_with_rules(ticker, company, filing_year, text)
    if provider == "openai":
        if prompt_path is None:
            raise ValueError("prompt_path is required for provider='openai'.")
        return score_with_openai(
            ticker=ticker,
            company=company,
            filing_year=filing_year,
            text=text,
            prompt=load_prompt(prompt_path),
            model=model,
        )
    raise ValueError(f"Unknown provider: {provider}")
