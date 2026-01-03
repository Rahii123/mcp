import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("WeatherAlerts")

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Fetch active weather alerts for a given US state (e.g., 'CA', 'NY')."""
    state = state.strip()
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
        for feature in features[:5]:  # Limit to 5 alerts for brevity
            props = feature.get("properties", {})
            alerts.append(f"- {props.get('headline', 'N/A')}")
            
        return "\n".join(alerts)

@mcp.resource("notes://general")
def get_notes() -> str:
    """A sample resource providing general information about the server."""
    return "This MCP server provides real-time weather alerts using the National Weather Service API."

if __name__ == "__main__":
    mcp.run()
