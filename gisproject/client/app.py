import anyio

from client import MCPClient


SERVER_URL = "http://localhost:8000/mcp"


async def test_calculate_area(client: MCPClient) -> None:
    result = await client.execute_tool(
        "calculate_area",
        {
            "payload": {
                "wkt_geometry": (
                    "POLYGON ((82 25, "
                    "82.01 25, "
                    "82.01 25.01, "
                    "82 25.01, "
                    "82 25))"
                ),
                "crs": "EPSG:4326",
            }
        },
    )

    print("Tool result:")
    print(result)


async def get_resource(client: MCPClient) -> None:
    resource = await client.get_resource(
    "gisprojection://available"
    )

    print(resource.uri)
    print(resource.name)
    print(resource.description)


async def main() -> None:
    client = MCPClient(SERVER_URL)

    print("Before connection:")
    print(client.is_connected)

    async with client:
        print("Inside context:")
        print(client.is_connected)

        # await test_calculate_area(client)
        await get_resource(client)

    print("After context:")
    print(client.is_connected)


if __name__ == "__main__":
    anyio.run(main)