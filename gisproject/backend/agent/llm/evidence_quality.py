from typing import Literal

from pydantic import BaseModel, Field


class EvidenceQuality(BaseModel):

    quality: Literal[
        "strong",
        "acceptable",
        "weak",
    ] = Field(
        description="Overall quality of the available evidence."
    )

    citation_valid: bool = Field(
        description="Whether the evidence can support citations for the answer."
    )

    errors: list[str] = Field(
        default_factory=list,
        description="Problems with the evidence or citations."
    )
def make_evidence_quality_evaluator(llm):

    evaluator = llm.with_structured_output(
        EvidenceQuality
    )

    async def evaluate(
        query: str,
        evidence: list[dict],
    ) -> EvidenceQuality:

        prompt = f"""
You are evaluating evidence for a GIS research assistant.

User question:
{query}

Evidence:
{evidence}

Check:

1. Does the evidence actually support the answer?
2. Is the evidence specific enough?
3. For web evidence, is there a usable source?
4. Are important claims unsupported?
5. Can the final answer cite the evidence?

Return the structured evaluation.
"""

        result = await evaluator.ainvoke(prompt)

        print("QUALITY TYPE:", type(result))
        print("QUALITY RESULT:", result)

        return result

    return evaluate