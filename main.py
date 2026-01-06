from mcp.server.fastmcp import FastMCP
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# 1. Load environment variables
load_dotenv()

# 2. Initialize FastMCP
mcp = FastMCP("AdvancedWeatherNews")

# 3. Define Tools
@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Fetch active weather alerts for a given US state (e.g., 'CA', 'NY')."""
    state = state.strip().upper()
    url = f"https://api.weather.gov/alerts/active/area/{state}"
    headers = {"User-Agent": "MCP-Server-Project (https://github.com/Rahii123/mcp)"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error fetching alerts: {response.status_code}"
        
        data = response.json()
        features = data.get("features", [])
        if not features:
            return f"No active weather alerts for {state}."
        
        alerts = []
        for feature in features[:5]:
            props = feature.get("properties", {})
            alerts.append(f"- {props.get('headline', 'N/A')}")
        return "\n".join(alerts)

@mcp.tool()
async def search_news(query: str) -> str:
    """Search for recent news articles on a specific topic."""
    query = query.strip()
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Error: NEWS_API_KEY not set in Railway Variables."
    
    url = f"https://newsapi.org/v2/everything?q={query}&pageSize=5&apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return f"Error fetching news: {response.status_code}"
        
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            return f"No news found for '{query}'."
        
        news_list = []
        for art in articles:
            news_list.append(f"- {art.get('title')} (Source: {art.get('source', {}).get('name')})")
        return "\n".join(news_list)

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List the contents of a local directory."""
    try:
        items = os.listdir(path)
        return "\n".join([f"- {item}" for item in items]) if items else "Directory is empty."
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Create the SSE app for Railway
app = mcp.sse_app

# 5. Add Health Check (Required for Railway)
@app.route("/")
async def homepage(request):
    return PlainTextResponse("MCP Server is Live!")

# 6. Startup Logic
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # If we run locally with 'uv run main.py' and no PORT is set, use Stdio
    if not os.getenv("PORT"):
        mcp.run()
    else:
        # If on Railway, use uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
