import random
from fastmcp import FastMCP
import json

mcp = FastMCP(name='Simple Calculator Server')

@mcp.tool
def roll_dice(n_dice : int = 1) -> list[int]:
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    return a + b

@mcp.resource("info::/server")
def server_info() -> str:
    info = {
        "name": "Simple calculator server",
        "version" : "1.0.0",
        "description" : "A basic MCP server with math tools",
        "tools" : ["add", "dice"],
        "author" : "Sanjay"
    }

if __name__ == '__main__':
    mcp.run(transport="http", host="0.0.0.0", port=8000)