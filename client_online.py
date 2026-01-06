import asyncio
import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_online_client():
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
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code} {e.response.reason_phrase}")
        print(f"URL: {e.request.url}")
        print("This usually means Railway is having trouble routing to your app.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_online_client())
