from langchain_core.messages import HumanMessage


class QueryRewriter:

    def __init__(self, llm):
        self.llm = llm

    async def rewrite(self, query: str) -> str:

        prompt = f"""
        You are a search query optimization system.

        Rewrite the user's question into a concise,
        information-rich web search query.

        Preserve the original intent.

        Do not answer the question.

        User question:
        {query}

        Return only the rewritten search query.
        """

        response = await self.llm.ainvoke(
            [
                HumanMessage(content=prompt)
            ]
        )

        return response.content.strip()