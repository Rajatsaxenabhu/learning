from langchain_core.documents import Document
from langchain_core.messages import HumanMessage


class RetrievalEvaluator:

    def __init__(self, llm):
        self.llm = llm

    async def evaluate(
        self,
        query: str,
        documents: list[Document],
    ) -> dict:

        context = "\n\n".join(
            f"""
SOURCE: {doc.metadata.get("source", "")}
TITLE: {doc.metadata.get("title", "")}

CONTENT:
{doc.page_content}
"""
            for doc in documents
        )

        prompt = f"""
You are a retrieval evaluation system.

Determine whether the retrieved documents contain
enough information to answer the user's question.

User question:
{query}

Retrieved documents:
{context}

Return ONLY valid JSON:

{{
    "sufficient": true or false,
    "reason": "short explanation",
    "missing_information": "what information is missing"
}}

Rules:

- sufficient=true only if the retrieved documents contain
  enough relevant information to answer the question.
- sufficient=false if important information is missing.
- Do not answer the user's question.
- Do not use your own knowledge.
- Evaluate ONLY the retrieved documents.
"""

        response = await self.llm.ainvoke(
            [HumanMessage(content=prompt)]
        )

        return self._parse_response(response.content)

    @staticmethod
    def _parse_response(content: str) -> dict:
        import json

        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        return json.loads(content)