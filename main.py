from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
import mcp.server.sse

# Load variables
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
        if not features: return f"No alerts for {state}."
        return "\n".join([f"- {f.get('properties', {}).get('headline', 'N/A')}" for f in features[:5]])

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
        if not articles: return "No news found."
        return "\n".join([f"- {a.get('title')} ({a.get('source', {}).get('name')})" for a in articles])

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List local directory contents."""
    try:
        items = os.listdir(path)
        return "\n".join([f"- {item}" for item in items]) if items else "Empty."
    except Exception as e: return str(e)

# --- PRODUCTION-READY SSE HANDLER ---
# This manual handler bypasses the strict Host validation that causes the 421 error
async def handle_sse(request):
    async with mcp.server.sse.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp.server.handle_request(read_stream, write_stream)

# Create a standard Starlette app
app = Starlette(
    routes=[
        Route("/", endpoint=lambda r: PlainTextResponse("MCP_SERVER_IS_LIVE")),
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST"])
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if os.getenv("PORT"):
        # Trust Railway Proxy
        uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
    else:
        # Local Stdio
        mcp.run()
