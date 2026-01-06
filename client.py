import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # Define the server parameters
    # This assumes 'uv run server.py' is how the server is executed
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
        env=None
    )

    print("--- Connecting to MCP Server ---")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize the session
            await session.initialize()
            print("Connected! Type 'exit' to quit.")

            while True:
                print("\n" + "="*30)
                print("What would you like to do?")
                print("1. Get Weather Alerts")
                print("2. Search News")
                print("3. List Directory")
                print("4. Exit")
                
                choice = input("\nEnter choice (1-4): ").strip()

                if choice == '1':
                    state = input("Enter US State (e.g., CA, NY): ").strip()
                    result = await session.call_tool("get_weather_alerts", arguments={"state": state})
                    print(f"\n[Weather for {state}]:\n{result.content[0].text if result.content else 'No alerts.'}")
                
                elif choice == '2':
                    query = input("Enter news topic: ").strip()
                    result = await session.call_tool("search_news", arguments={"query": query})
                    print(f"\n[News for {query}]:\n{result.content[0].text if result.content else 'No news found.'}")
                
                elif choice == '3':
                    path = input("Enter path (or press enter for current): ").strip() or "."
                    result = await session.call_tool("list_directory", arguments={"path": path})
                    print(f"\n[Files in {path}]:\n{result.content[0].text if result.content else 'Empty directory.'}")
                
                elif choice == '4' or choice.lower() == 'exit':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice, try again.")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\nClient stopped.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
