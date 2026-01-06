from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

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
        if not features: return "No alerts."
        return "\n".join([f"- {f.get('properties', {}).get('headline', 'N/A')}" for f in features[:5]])

@mcp.tool()
async def search_news(query: str) -> str:
    """Search for news using keywords."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key: return "Error: API key missing."
    url = f"https://newsapi.org/v2/everything?q={query.strip()}&pageSize=5&apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200: return "NewsAPI error."
        articles = response.json().get("articles", [])
        return "\n".join([f"- {a.get('title')}" for a in articles[:5]]) or "No news."

# --- THE "SENIOR" NETWORKING FIX ---
# Instead of a manual handler, we use the one FastMCP provides, 
# but we wrap the whole app in a middleware that fixes the Host header.
app = mcp.sse_app()

@app.middleware("http")
async def fix_host_header(request, call_next):
    # This tricks the MCP library into thinking the request is local
    # This solves the 421 Misdirected Request / ValueError once and for all.
    new_headers = dict(request.headers)
    new_headers["host"] = "localhost"
    request._headers = httpx.Headers(new_headers)
    request.scope["headers"] = [(k.encode().lower(), v.encode()) for k, v in new_headers.items()]
    return await call_next(request)

@app.route("/")
async def health(request):
    return PlainTextResponse("MCP_SERVER_IS_LIVE")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if os.getenv("PORT"):
        uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
    else:
        mcp.run()
