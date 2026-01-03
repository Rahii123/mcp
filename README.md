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

### Testing with MCP Inspector
To interactively test the tools:
```bash
npx @modelcontextprotocol/inspector python server.py
```

## 📜 License
MIT
