from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("test")
print("Attributes containing 'app':")
for attr in dir(mcp):
    if "app" in attr.lower():
        print(attr)
