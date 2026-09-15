from mcp import Client
from mcp.types import ListResourcesResult, ListToolsResult
from error import MCPToolNotFoundError,MCPResourceNotFoundError,MCPToolError,MCPResourceError,MCPConnectionError,MCPClientError
from typing import Any

class MCPClient:

    def __init__(self, transport: Any):
        self.transport = transport

        self._client: Client | None = None

        self._tools: ListToolsResult | None = None
        self._resources: ListResourcesResult | None = None


    async def __aenter__(self):
        client = Client(self.transport)

        try:
            await client.__aenter__()

        except Exception as exc:
            self._client = None

            raise MCPConnectionError(
                f"Failed to connect to MCP server: "
                f"{self.transport}"
            ) from exc

        self._client = client
        self._tools = None
        self._resources = None

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if self._client is not None:
            try:
                await self._client.__aexit__(
                    exc_type,
                    exc_value,
                    traceback,
                )
            finally:
                self._client = None
                self._tools = None
                self._resources = None


    @property
    def is_connected(self) -> bool:
        return self._client is not None

    @property
    def mcp_client(self) -> Client:
        if self._client is None:
            raise MCPConnectionError(
                "MCP client is not connected. "
                "Use 'async with MCPClient(...)'."
            )

        return self._client
    
    async def refresh_tools(self) -> ListToolsResult:
        try:
            result = await self.mcp_client.list_tools()

        except Exception as exc:
            raise MCPToolError(
                "Failed to discover MCP tools."
            ) from exc

        self._tools = result

        return result

    async def list_tools(self) -> ListToolsResult:
        if self._tools is None:
            return await self.refresh_tools()

        return self._tools

    async def get_tool(self, name: str):

        tools = await self.list_tools()

        for tool in tools.tools:
            if tool.name == name:
                return tool

        raise MCPToolNotFoundError(
            f"MCP tool '{name}' not found."
        )

    async def call_tool(
        self,
        name: str,
        arguments: dict,
    ):
        try:
            return await self.mcp_client.call_tool(
                name,
                arguments,
            )

        except Exception as exc:
            raise MCPToolError(
                f"Failed to call MCP tool '{name}'."
            ) from exc

    async def execute_tool(
        self,
        name: str,
        arguments: dict,
    ):

        await self.get_tool(name)

        try:
            result = await self.call_tool(
                name,
                arguments,
            )

        except Exception as exc:
            raise MCPToolError(
                f"Failed to execute MCP tool '{name}'."
            ) from exc

        if result.is_error:
            raise MCPToolError(
                f"MCP tool '{name}' returned an error: "
                f"{result.content}"
            )

        return result.structured_content


    async def refresh_resources(self) -> ListResourcesResult:
        try:
            result = await self.mcp_client.list_resources()

        except Exception as exc:
            raise MCPResourceError(
                "Failed to discover MCP resources."
            ) from exc

        self._resources = result

        return result

    async def list_resources(self) -> ListResourcesResult:
        if self._resources is None:
            return await self.refresh_resources()

        return self._resources

    async def get_resource(self, uri: str):

        resources = await self.list_resources()

        for resource in resources.resources:
            if str(resource.uri) == uri:
                return resource

        raise MCPResourceNotFoundError(
            f"MCP resource '{uri}' not found."
        )

    async def read_resource(self, uri: str):
        
        await self.get_resource(uri)

        try:
            return await self.mcp_client.read_resource(uri)

        except Exception as exc:
            raise MCPResourceError(
                f"Failed to read MCP resource '{uri}'."
            ) from exc

