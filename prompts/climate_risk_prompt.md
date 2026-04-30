You are extracting climate risk signals from corporate disclosures for an empirical asset pricing project.

Return strict JSON with this schema:

{
  "physical_risk_score": integer 0-5,
  "transition_risk_score": integer 0-5,
  "litigation_risk_score": integer 0-5,
  "opportunity_score": integer 0-5,
  "overall_climate_risk_score": number 0-5,
  "confidence": number 0-1,
  "evidence": ["short cited evidence phrase 1", "short cited evidence phrase 2"]
}

Scoring rubric:
- 0: no meaningful mention
- 1: vague or boilerplate mention
- 2: limited but identifiable exposure
- 3: material exposure
- 4: high exposure
- 5: severe exposure central to business model

Definitions:
- Physical risk: acute or chronic climate effects such as hurricanes, floods, wildfires, droughts, heat, water stress, and supply chain disruption.
- Transition risk: regulation, carbon pricing, emissions standards, energy transition, stranded assets, changing demand, and technology substitution.
- Litigation risk: climate lawsuits, environmental claims, disclosure risk, and compliance disputes.
- Opportunity: revenue or strategic upside from renewable energy, efficiency, electrification, adaptation, green infrastructure, or low-carbon products.

Rules:
- Score actual disclosed risk, not whether the company is "good" or "bad" on climate.
- Do not reward vague sustainability language unless it connects to business exposure.
- Keep evidence short and grounded in the provided text.
- Return JSON only.
