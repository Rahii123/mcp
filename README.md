# 🚀 Advanced MCP Server

A professional Model Context Protocol (MCP) server built with Python and FastMCP. This server extends AI capabilities by providing real-time data and local system access.

## ✨ Features

- **🌦️ Weather Alerts**: Fetches active US weather alerts from the National Weather Service.
- **📰 News Search**: Real-time news searching using the NewsAPI.
- **📁 Directory Explorer**: Allows the AI to list and explore local system directories safely.
- **🔐 Secure Secrets**: Uses `.env` for safe API key management.

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Rahii123/mcp.git
   cd mcp
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```

### Setup
Create a `.env` file in the root directory and add your NewsAPI key:
```env
NEWS_API_KEY=your_actual_key_here
```

## 🚀 Running the Server

Run directly with `uv`:
```bash
uv run server.py
```

## 🧪 Testing Your Server

We have provided two separate clients for testing:

### 🏠 1. Local Testing (Stdio)
Use this when you are developing on your own machine.
```bash
uv run client_local.py
```
*This starts the server as a background process and communicates directly.*

### 🌐 2. Online Testing (SSE)
Use this after you have deployed your server to the web (e.g., Railway).
```bash
uv run client_online.py
```
*This asks for your deployment URL and connects over the internet.*

---

## ☁️ Deployment to Railway (Step-by-Step)

### 1. Push to GitHub
Ensure all your changes are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Connect to Railway
1. Go to [Railway.app](https://railway.app/) and log in.
2. Click **+ New Project** > **Deploy from GitHub repo**.
3. Select your `mcp` repository.

### 3. Configure the Service
1. **Environment Variables**:
   - Go to the **Variables** tab in Railway.
   - Add `NEWS_API_KEY`: `(Your actual NewsAPI Key)`
2. **Start Command**:
   - Railway should automatically detect `pyproject.toml`, but if needed, set the start command to:
     ```bash
     uv run server.py
     ```
3. **Networking**:
   - Railway will automatically detect the port from the `$PORT` environment variable. Ensure your `server.py` is using `mcp.run(transport='sse')` (I've already configured this for you).

### 4. Fetch your URL
Once the build is finished, Railway will provide a public URL (e.g., `https://mcp-production.up.railway.app`). 
The MCP endpoint will be at: `https://your-app-url.up.railway.app/sse`

---
