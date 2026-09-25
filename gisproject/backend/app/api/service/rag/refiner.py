from langchain_core.messages import HumanMessage


class QueryRefiner:

    def __init__(self, llm):
        self.llm = llm

    async def refine(
        self,
        original_query: str,
        missing_information: str,
    ) -> str:

        prompt = f"""
You are a web search query optimization system.

The original user question is:

{original_query}

The retrieved documents were insufficient.

The missing information is:

{missing_information}

Create a new web search query that specifically searches
for the missing information.

Rules:

- Preserve the user's original intent.
- Focus on the missing information.
- Make the query concise and information-rich.
- Do not answer the question.
- Return ONLY the search query.
"""

        response = await self.llm.ainvoke(
            [HumanMessage(content=prompt)]
        )

        return response.content.strip()