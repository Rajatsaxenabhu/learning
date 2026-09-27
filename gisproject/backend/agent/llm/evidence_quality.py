from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal


class EvidenceQuality(BaseModel):

    quality: Literal[
        "strong",
        "acceptable",
        "weak",
    ] = Field(
        description="Overall quality of the available evidence."
    )

    citation_valid: bool = Field(
        description=(
            "Whether the evidence can support "
            "citations for the answer."
        )
    )

    errors: list[str] = Field(
        default_factory=list,
        description=(
            "Problems with the evidence or citations."
        ),
    )


def make_evidence_quality_evaluator(llm):

    evaluator = llm.with_structured_output(
        EvidenceQuality,
        method="function_calling",
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

Evaluate the evidence.

Check:

1. Does the evidence actually support the answer?
2. Is the evidence specific enough?
3. For web evidence, is there a usable source?
4. Are important claims unsupported?
5. Can the final answer cite the evidence?

Return ONLY the structured result.

If the evidence is sufficient:
- quality = "strong" or "acceptable"
- citation_valid = true
- errors = []

If the evidence is insufficient:
- quality = "weak"
- citation_valid = false
- errors must explain why.
"""

        try:

            result = await evaluator.ainvoke(
                [
                    HumanMessage(
                        content=prompt
                    )
                ]
            )

            if result is None:
                return EvidenceQuality(
                    quality="weak",
                    citation_valid=False,
                    errors=[
                        "Evidence quality evaluator "
                        "returned no result."
                    ],
                )

            return result

        except Exception as e:

            return EvidenceQuality(
                quality="weak",
                citation_valid=False,
                errors=[
                    f"Evidence quality evaluation "
                    f"failed: {e}"
                ],
            )

    return evaluate

