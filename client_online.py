import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_online_client():
    # REPLACE THIS URL with your actual Railway deployment URL
    # Example: "https://mcp-server-production-xxxx.up.railway.app/sse"
    url = input("Enter your deployed MCP Server URL (including /sse): ").strip()
    
    if not url.startswith("http"):
        print("Error: URL must start with http:// or https://")
        return

    print(f"--- [ONLINE] Connecting to MCP Server via SSE at {url} ---")
    
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected! Type 'exit' to quit.")

                while True:
                    print("\n" + "="*30)
                    print("Online Control Menu:")
                    print("1. Get Weather Alerts")
                    print("2. Search News")
                    print("3. List Directory (Remote)")
                    print("4. Exit")
                    
                    choice = input("\nEnter choice: ").strip()

                    if choice == '1':
                        state = input("Enter US State (e.g., CA): ").strip()
                        result = await session.call_tool("get_weather_alerts", arguments={"state": state})
                        print(f"\nResult:\n{result.content[0].text if result.content else 'No data'}")
                    elif choice == '2':
                        query = input("Enter news topic: ").strip()
                        result = await session.call_tool("search_news", arguments={"query": query})
                        print(f"\nResult:\n{result.content[0].text if result.content else 'No news'}")
                    elif choice == '3':
                        path = input("Enter path: ").strip() or "."
                        result = await session.call_tool("list_directory", arguments={"path": path})
                        print(f"\nResult:\n{result.content[0].text if result.content else 'Empty'}")
                    elif choice == '4' or choice.lower() == 'exit':
                        break
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_online_client())
