class MCPClientError(RuntimeError):
    """Base exception for MCP client errors."""


class MCPConnectionError(MCPClientError):
    """MCP server connection failed."""


class MCPToolError(MCPClientError):
    """MCP tool execution failed."""


class MCPToolNotFoundError(MCPToolError):
    """Requested MCP tool does not exist."""


class MCPResourceError(MCPClientError):
    """MCP resource operation failed."""


class MCPResourceNotFoundError(MCPResourceError):
    """Requested MCP resource does not exist."""