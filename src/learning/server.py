from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel,Field
from mcp.types import EmbeddedResource, TextResourceContents
from mcp.server.mcpserver import Image,AssistantMessage,Message,UserMessage

mcp = MCPServer("Bookshop")

CATALOG = {
    "Dune": "Frank Herbert",
    "Neuromancer": "William Gibson",
    "The Left Hand of Darkness": "Ursula K. Le Guin",
}


@mcp.tool()
def search_books(name:str)->list[tuple[dict, dict]]:
    """search the book using the title """
    query=name.lower()
    return [({"title": title}, {"author": author}) for title, author in CATALOG.items() if query in title.lower()]

class Books(BaseModel):
    Name:str=Field(description="enter the book name")
    Author:str=Field(description="enter the name of the author")


@mcp.tool(
        title="insert the new book in the catalog "
)
def insert_book(payload:Books)->list[Books]:
    """ this will insert the books in the catalogs """
    global CATALOG
    CATALOG[payload.Name] = payload.Author
    return [Books(Name=name, Author=author) for name, author in CATALOG.items()]


@mcp.resource("books://{findname}")
def titles(findname: str) -> str:
    """ return the author for a given book title"""
    if findname not in CATALOG:
        raise ToolError(f"No book titled '{findname}' found")
    return CATALOG[findname]
        

@mcp.prompt(title="user promts")
def debugs(error:str)->list[Message]:
    """start the debugging """
    return [
        UserMessage("I'm seeing this error:"),
        UserMessage(error),
        AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

from mcp.server.mcpserver.resources import ResourceSecurity

@mcp.resource(
    "file://readfile/{+file_path}",   # {+...} allows slashes in the value
    title="read file",
    mime_type="text/markdown",
    security=ResourceSecurity(reject_absolute_paths=False),  # you're intentionally passing full paths
)
def read_file(file_path: str) -> str:
    """Read a file from disk given its path."""
    return Path(file_path).read_text(encoding="utf-8")


@mcp.prompt(title="Image gen")
def Image_gen(file_path: str,image_path:str) -> list[Message]:
    """Image generate from the file context"""
    guide = TextResourceContents(
        uri=f"names",
        mime_type="text/markdown",
        text=read_file(file_path),
    )
    return[
        UserMessage(f"generate the image like this "),
        UserMessage(EmbeddedResource(resource=guide)),
        AssistantMessage(f"Image generate successfuly"),
        UserMessage(Image(path=image_path)),
        UserMessage(f"this image is wring")
    ]
if __name__ == "__main__":
    mcp.run()