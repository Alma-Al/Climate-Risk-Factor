from __future__ import annotations

from climate_risk_factor.llm_extractor import score_with_rules


def test_rules_extractor_separates_transition_and_opportunity() -> None:
    text = (
        "Emissions regulation, carbon price policies, and decarbonization may "
        "increase capital expenditure. Renewable energy and clean technology "
        "also create low-carbon growth opportunities."
    )

    score = score_with_rules("TST", "Test Co", 2024, text)

    assert score.transition_risk_score >= 3
    assert score.opportunity_score >= 2
    assert score.overall_climate_risk_score > 0
    assert score.evidence


def test_rules_extractor_keeps_boilerplate_low() -> None:
    text = (
        "The company monitors environmental compliance and disclosure practices. "
        "No material climate-related physical or transition exposure was identified."
    )

    score = score_with_rules("LOW", "Low Risk Co", 2024, text)

    assert score.overall_climate_risk_score <= 1.5
    assert score.physical_risk_score <= 1
