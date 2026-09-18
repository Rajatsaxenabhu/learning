import sys
from pathlib import Path

import anyio

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)

from langchain_openai import ChatOpenAI
from agent.llm.config import ModelConfig
from agent.tools import create_mcp_tool
from langchain.agents import create_agent

from client.manager import MCPClientManager
from client.config import GIS_STDIO_SERVER as GIS_SERVER
model = ChatOpenAI(
    model=ModelConfig.model,
    base_url=ModelConfig.base_url,
    api_key=ModelConfig.api_key,
)

async def main():
    async with MCPClientManager([GIS_SERVER]) as manager:
        client = manager.get("gis_local")
        mcp_tools = await client.list_tools()
        print("MCP tools:", len(mcp_tools.tools))
    
        langchain_tools = [
            create_mcp_tool(
                manager,
                "gis_local",
                tool,
            )
            for tool in mcp_tools.tools
        ]
        print("LangChain tools:", len(langchain_tools))

        for tool in langchain_tools:
            print(tool.name)
        agent = create_agent(
            model=model,
            tools=langchain_tools,
        )
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Calculate the area of this polygon. "
                            "The geometry is "
                            "POLYGON ((82 25, 82.01 25, 82.01 25.01, 82 25)) "
                            "and the CRS is EPSG:4326."
                        ),
                    }
                ]
            }
        )
        print(result["messages"][-1].content)
if __name__ == "__main__":
    anyio.run(main)