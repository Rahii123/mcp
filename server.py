from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
# Note: For Railway/Deployment, the server name/title is mainly for UI
mcp = FastMCP("AdvancedWeatherNews")

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Fetch active weather alerts for a given US state (e.g., 'CA', 'NY')."""
    # API requires uppercase state codes (e.g., 'CA' not 'ca')
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
    if not api_key or api_key.strip() == "your_api_key_here":
        return "Error: NEWS_API_KEY not set. Please add it to your .env file."
    
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
    """List the contents of a local directory. Default is current directory."""
    try:
        items = os.listdir(path)
        if not items:
            return f"The directory '{path}' is empty."
        
        return "\n".join([f"- {item}" for item in items])
    except Exception as e:
        return f"Error reading directory: {str(e)}"

if __name__ == "__main__":
    # Railway sets a PORT environment variable automatically
    port = int(os.getenv("PORT", 8000))
    
    if os.getenv("PORT"):
        print(f"Starting SSE server on 0.0.0.0:{port}...")
        # Listening on 0.0.0.0 is required for most cloud providers like Railway
        mcp.run(transport='sse', host="0.0.0.0", port=port)
    else:
        # Default to stdio for local development
        print("Starting local Stdio server...")
        mcp.run(transport='stdio')
