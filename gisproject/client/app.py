import anyio

from manager import MCPClientManager, MCPClient
from config import GIS_STDIO_SERVER


async def test_calculate_area(client: MCPClient) -> None:
    result = await client.execute_tool(
        "calculate_area",
        {
            "payload": {
                "wkt_geometry": (
                    "POLYGON ((82 25, "
                    "82.01 25, "
                    "82.01 25.01, "
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

    print("URI:", resource.uri)
    print("Name:", resource.name)
    print("Description:", resource.description)

    result = await client.read_resource(
        str(resource.uri)
    )

    print("Resource data:")
    print(result)


async def main() -> None:

    async with MCPClientManager([GIS_STDIO_SERVER]) as manager:

        gis = manager.get("gis_local")

        print("Inside manager context:")
        print("GIS connected:", gis.is_connected)

        await test_calculate_area(gis)

        await get_resource(gis)

    print("After manager context:")
    print("GIS connected:", gis.is_connected)


if __name__ == "__main__":
    anyio.run(main)