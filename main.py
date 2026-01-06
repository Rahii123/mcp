from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

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

# --- RAILWAY & NETWORKING FIX ---
# 1. Create the App instance
app = mcp.sse_app()

# 2. Add The "Senior Engineer" Middleware Fix
class HostFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # This fixes the "421 Misdirected Request" by making the host header
        # match what the MCP library expects from Railway.
        if "x-forwarded-host" in request.headers:
            host = request.headers["x-forwarded-host"]
            new_headers = []
            for name, value in request.scope["headers"]:
                if name.lower() == b"host":
                    new_headers.append((b"host", host.encode()))
                else:
                    new_headers.append((name, value))
            request.scope["headers"] = new_headers
        return await call_next(request)

app.add_middleware(HostFixMiddleware)

@app.route("/")
async def homepage(request):
    return PlainTextResponse("MCP_SERVER_IS_LIVE")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    # If no PORT is set (local testing), use mcp.run()
    if not os.getenv("PORT"):
        mcp.run()
    else:
        # On Railway, use uvicorn with proxy settings
        uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
