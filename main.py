from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from mcp.server.sse import SseServerTransport
from mcp.server.transport_security import TransportSecuritySettings

# --- VERSION TRACKING ---
# Look for this in your Railway logs to confirm the NEW code is running
VERSION = "FINAL_BULLETPROOF_V4"
print(f"--- STARTING MCP SERVER VERSION: {VERSION} ---")

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

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List local directory contents."""
    try:
        items = os.listdir(path)
        return "\n".join([f"- {item}" for item in items]) if items else "Empty."
    except Exception as e: return str(e)

# --- THE "BULLETPROOF" TRANSPORT FIX ---
# We explicitly disable the security check that causes the 421/ValueError
security_settings = TransportSecuritySettings(enable_dns_rebinding_protection=False)
sse = SseServerTransport("/sse", security_settings=security_settings)

async def handle_sse(request):
    # Defensive attribute access: handle both old and new FastMCP versions
    internal_server = getattr(mcp, "_mcp_server", getattr(mcp, "server", None))
    if internal_server is None:
        raise AttributeError("Could not find the internal MCP server in FastMCP object")
    
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await internal_server.handle_request(read, write)

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# --- STARLETTE APP ---
app = Starlette(
    routes=[
        Route("/", endpoint=lambda r: PlainTextResponse(f"MCP_SERVER_IS_LIVE (Ver: {VERSION})")),
        Route("/sse", endpoint=handle_sse),
        # Note: the message endpoint MUST match what SseServerTransport was initialized with
        Route("/sse", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if os.getenv("PORT"):
        uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
    else:
        mcp.run()
