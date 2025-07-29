import base64
import os
from typing import Any
from typing import Dict

import requests
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

BING_API_KEY = os.getenv("BING_API_KEY")
if not BING_API_KEY:
    pass
    # raise RuntimeError("Set BING_API_KEY env var for Bing Visual Search API access")

mcp = FastMCP("Visor Image Metadata")


def _bing_reverse_search(image_bytes: bytes) -> Dict[str, Any]:
    """Call Bing Visual Search and return the raw JSON."""
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    resp = requests.post(
        "https://api.bing.microsoft.com/v7.0/images/visualsearch",
        headers=headers,
        files={"image": ("img.jpg", image_bytes, "image/jpeg")},
    )
    resp.raise_for_status()
    return resp.json()


def _extract_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Bing response into Metadata-compatible dict."""
    if not raw.get("tags"):
        return {}
    first = raw["tags"][0]["actions"][0]["data"]["value"][0]
    tags = [t.get("displayName", "") for t in raw.get("tags", [])]
    return {
        "title": first.get("name", ""),
        "author": first.get("hostPageDisplayUrl", "").split("/")[-2],
        "year": "",
        "description": first.get("name", ""),
        "tags": tags,
        "museum": "",
        "material": "",
        "source": first.get("hostPageUrl", ""),
    }

@mcp.tool()
def search_image_metadata(image_b64: str) -> Dict[str, Any]:
    """Return best-guess metadata for a base64-encoded image."""
    raw = _bing_reverse_search(base64.b64decode(image_b64))
    return _extract_metadata(raw)


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}!"


# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)
