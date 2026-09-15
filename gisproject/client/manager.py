from connect.base import MCPClient
from config import MCPServerConfig


class MCPClientManager:

    def __init__(
        self,
        servers: list[MCPServerConfig],
    ):
        self.servers = servers
        self._clients: dict[str, MCPClient] = {}

    async def __aenter__(self):
        for server in self.servers:
            client = MCPClient(server.transport)

            await client.__aenter__()

            self._clients[server.name] = client

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        for client in self._clients.values():
            await client.__aexit__(
                exc_type,
                exc_value,
                traceback,
            )

        self._clients.clear()

    def get(self, name: str) -> MCPClient:
        client = self._clients.get(name)

        if client is None:
            raise KeyError(
                f"MCP server '{name}' is not connected."
            )

        return client

    def names(self) -> list[str]:
        return list(self._clients.keys())