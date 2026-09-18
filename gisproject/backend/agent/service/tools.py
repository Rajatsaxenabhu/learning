import json

from typing import Any

from pydantic import create_model, Field
from langchain_core.tools import StructuredTool, ToolException


def create_args_schema(mcp_tool):
    schema = mcp_tool.input_schema

    payload_schema = schema["properties"]["payload"]

    ref = payload_schema.get("$ref")

    if ref:
        payload_schema = schema["$defs"][ref.rsplit("/", 1)[-1]]

    properties = payload_schema.get("properties", {})
    required = set(payload_schema.get("required", []))

    fields = {}

    for name, definition in properties.items():
        field_type = str

        fields[name] = (
            field_type if name in required else field_type | None,
            Field(
                default=... if name in required else None,
                description=definition.get("description", ""),
            ),
        )

    return create_model(
        f"{mcp_tool.name}Input",
        **fields,
    )


def create_mcp_tool(
    mcp_manager,
    server_name: str,
    mcp_tool,
):
    args_schema = create_args_schema(mcp_tool)

    async def call_mcp_tool(**kwargs: Any):
        client = mcp_manager.get(server_name)

        result = await client.call_tool(
            mcp_tool.name,
            {
                "payload": kwargs,
            },
        )

        if result.structured_content is not None:
            text = json.dumps(result.structured_content)
        else:
            text = "\n".join(
                block.text
                for block in result.content
                if getattr(block, "text", None)
            )

        if result.is_error:
            raise ToolException(text or "Tool call failed")

        return text

    return StructuredTool.from_function(
        coroutine=call_mcp_tool,
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        args_schema=args_schema,
    )

async def discover_tools(
    mcp_manager,
    server_name: str,
):
    client = mcp_manager.get(server_name)

    mcp_tools = await client.list_tools()

    langchain_tools = [
        create_mcp_tool(
            mcp_manager,
            server_name,
            mcp_tool,
        )
        for mcp_tool in mcp_tools.tools
    ]

    return langchain_tools