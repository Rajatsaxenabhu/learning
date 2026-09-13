import anyio
from client import MCPClient

server_url="http://localhost:8000/mcp"
async def main():
    async with MCPClient(server_url) as client_obj:
        print("SERVER INFO")
        print(client_obj.client.server_info)

        print("\nSERVER CAPABILITIES")
        print(client_obj.client.server_capabilities)

        print("\nPROTOCOL VERSION")
        print(client_obj.client.protocol_version)

        print("\nSERVER INSTRUCTIONS")
        print(client_obj.client.instructions)




if __name__ == "__main__":
    anyio.run(main)