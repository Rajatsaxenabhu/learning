from mcp import Client


class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url

    async def __aenter__(self):
        self.client = Client(self.server_url)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )

    async def list_tools(self):
        return await self.client.list_tools()

    async def list_resources(self):
        return await self.client.list_resources()

    async def call_tool(self, name: str, arguments: dict):
        return await self.client.call_tool(
            name,
            arguments,
        )