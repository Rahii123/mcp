from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# Load local .env if it exists
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("AdvancedWeatherNews")

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Fetch active weather alerts for a given US state."""
    state = state.strip().upper()
    url = f"https://api.weather.gov/alerts/active/area/{state}"
    headers = {"User-Agent": "MCP-Server-Project (https://github.com/Rahii123/mcp)"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: API returned {response.status_code}"
        data = response.json()
        features = data.get("features", [])
        if not features: return f"No active alerts for {state}."
        return "\n".join([f"- {f.get('properties', {}).get('headline', 'N/A')}" for f in features[:5]])

@mcp.tool()
async def search_news(query: str) -> str:
    """Search for news using keywords."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key: return "Error: NEWS_API_KEY not found in environment."
    url = f"https://newsapi.org/v2/everything?q={query.strip()}&pageSize=5&apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200: return f"Error: {response.status_code}"
        articles = response.json().get("articles", [])
        if not articles: return "No news found."
        return "\n".join([f"- {a.get('title')} ({a.get('source', {}).get('name')})" for a in articles])

# --- RAILWAY CONFIGURATION ---
app = mcp.sse_app()

@app.route("/")
async def health_check(request):
    """Crucial for Railway to know the app is alive."""
    return PlainTextResponse("MCP_SERVER_IS_LIVE")

if __name__ == "__main__":
    # If Railway provides a PORT, use it and run in SSE mode
    port = int(os.getenv("PORT", 8080))
    if os.getenv("PORT"):
        # Use proxy_headers=True to handle Railway's load balancer correctly
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            proxy_headers=True, 
            forwarded_allow_ips="*"
        )
    else:
        # Default to local stdio mode
        mcp.run()
