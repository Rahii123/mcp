import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_local_client():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
        env=None
    )

    print("--- [LOCAL] Connecting to MCP Server via Stdio ---")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected! Type 'exit' to quit.")

            while True:
                print("\n" + "="*30)
                print("Local Control Menu:")
                print("1. Get Weather Alerts")
                print("2. Search News")
                print("3. List Directory")
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

if __name__ == "__main__":
    asyncio.run(run_local_client())
