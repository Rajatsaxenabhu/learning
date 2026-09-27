from typing import Literal

from pydantic import BaseModel, Field


class EvidenceEvaluation(BaseModel):
    sufficient: bool = Field(
        description="Whether the available evidence is sufficient to answer the user's question."
    )

    reason: str = Field(
        description="Why the evidence is or is not sufficient."
    )

    next_action: Literal[
        "answer",
        "search_knowledge",
        "web_rag",
        "gis_tool",
    ] = Field(
        description="What should happen next if the evidence is insufficient."
    )

def make_evidence_evaluator(llm):

    evaluator = llm.with_structured_output(
        EvidenceEvaluation
    )

    async def evaluate(
        query: str,
        evidence: list[dict],
    ) -> EvidenceEvaluation:

        prompt = f"""
You are an evidence evaluator for a GIS research agent.

User question:
{query}

Available evidence:
{evidence}

Determine whether the evidence is sufficient to answer
the user's question accurately.

Rules:

- Do not judge whether the answer sounds plausible.
- Check whether the evidence actually supports the answer.
- If important information is missing, mark insufficient.
- If sufficient, choose "answer".
- If insufficient, select the most appropriate next capability:
  - search_knowledge
  - web_rag
  - gis_tool

Return only the structured evaluation.
"""
        result = await evaluator.ainvoke(prompt)
        return result
    

    return evaluate