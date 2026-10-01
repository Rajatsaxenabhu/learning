from agent.llm.graph import build_graph
from agent.rag.main import WebRAG
from agent.service.knowledge import create_knowledge_retriever
from client.config import GIS_STDIO_SERVER,GEE_STDIO_SERVER
from client.manager import MCPClientManager
from langgraph.checkpoint.memory import InMemorySaver


class AgentRuntime:

    def __init__(self):

        self.checkpointer = InMemorySaver()

        self.mcp = MCPClientManager(
            [GIS_STDIO_SERVER,GEE_STDIO_SERVER]
        )

        self.web_rag = WebRAG(
            checkpointer=self.checkpointer
        )

        self.graph = None

        self.initialized = False

    async def initialize(self):

        if self.initialized:
            return

        await self.mcp.__aenter__()

        try:

            await self.web_rag.initialize()

            knowledge_retriever = (
                create_knowledge_retriever()
            )

            self.graph = await build_graph(
                self.mcp,
                web_rag=self.web_rag,
                knowledge_retriever=knowledge_retriever,
                checkpointer=self.checkpointer,
            )

            self.initialized = True

        except BaseException:

            await self.web_rag.close()

            await self.mcp.__aexit__(
                None,
                None,
                None,
            )

            raise

    async def close(self):

        if not self.initialized:
            return

        await self.web_rag.close()

        await self.mcp.__aexit__(
            None,
            None,
            None,
        )

        self.graph = None
        self.initialized = False