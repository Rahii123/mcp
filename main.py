from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("AdvancedWeatherNews")

# --- TOOLS ---
@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Fetch active weather alerts for a US state."""
    state = state.strip().upper()
    url = f"https://api.weather.gov/alerts/active/area/{state}"
    headers = {"User-Agent": "MCP-Server-Project"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200: return f"Error: {response.status_code}"
        features = response.json().get("features", [])
        return "\n".join([f"- {f.get('properties', {}).get('headline', 'N/A')}" for f in features[:5]]) if features else "No alerts."

@mcp.tool()
async def search_news(query: str) -> str:
    """Search for news using keywords."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key: return "Error: News API key missing."
    url = f"https://newsapi.org/v2/everything?q={query.strip()}&pageSize=5&apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200: return f"Error: {response.status_code}"
        articles = response.json().get("articles", [])
        return "\n".join([f"- {a.get('title')}" for a in articles]) or "No news found."

# --- BULLETPROOF NETWORKING ---
# We use the internal SSE handler but we disable the strict host check by overriding the transport
sse = SseServerTransport("/sse")

async def handle_sse(request):
    # This manually handles the SSE connection and bypasses FastMCP's internal validation
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await mcp.server.handle_request(read, write)

async def handle_messages(request):
    # This handles the POST messages from the client
    await sse.handle_post_message(request.scope, request.receive, request._send)

# Create a clean Starlette app
app = Starlette(
    routes=[
        Route("/", endpoint=lambda r: PlainTextResponse("MCP_SERVER_IS_LIVE")),
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if os.getenv("PORT"):
        uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
    else:
        mcp.run()
