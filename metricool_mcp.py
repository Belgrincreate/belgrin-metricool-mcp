#!/usr/bin/env python3
"""
Metricool MCP Server for Belgrin.
Set the METRICOOL_API_KEY environment variable before running.
"""

import os
import json
import httpx
import uvicorn
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("belgrin_metricool")

METRICOOL_API_KEY = os.environ.get("METRICOOL_API_KEY", "")
BASE_URL = "https://app.metricool.com/api/v2"

def _headers():
    return {"X-Mc-Auth": METRICOOL_API_KEY, "Content-Type": "application/json"}

def _check_key() -> Optional[str]:
    if not METRICOOL_API_KEY:
        return "Error: METRICOOL_API_KEY is not set on the server."
    return None

def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return "Error: Metricool API key rejected."
        elif status == 403:
            return "Error: Access forbidden."
        elif status == 404:
            return f"Error: Resource not found. Details: {e.response.text}"
        elif status == 429:
            return "Error: Rate limit reached. Wait 30 seconds and try again."
        return f"Error: API returned status {status}. Details: {e.response.text}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again."
    return f"Error: {type(e).__name__}: {str(e)}"

@mcp.tool(name="get_brands")
async def get_brands() -> str:
    """Get all Metricool brands. Always call this first to get blog_id values."""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs", headers=_headers())
            r.raise_for_status()
            data = r.json()
            simplified = [
                {"blog_id": b.get("id"), "name": b.get("name"), "url": b.get("url", ""), "networks": list(b.get("networks", {}).keys())}
                for b in (data if isinstance(data, list) else data.get("data", []))
            ]
            return json.dumps(simplified, indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_scheduled_posts")
async def get_scheduled_posts(blog_id: int) -> str:
    """Get all upcoming scheduled posts for a brand. Args: blog_id from get_brands()"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs/{blog_id}/posts/scheduled", headers=_headers())
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_best_time_to_post")
async def get_best_time_to_post(blog_id: int, network: str) -> str:
    """Get optimal posting times. network: linkedin, instagram, facebook, twitter, tiktok"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs/{blog_id}/analytics/besttime/{network}", headers=_headers())
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="post_schedule_post")
async def post_schedule_post(blog_id: int, network: str, text: str, publish_date: str, image_url: Optional[str] = None) -> str:
    """Schedule a post. publish_date format: YYYY-MM-DDTHH:MM:SS"""
    err = _check_key()
    if err:
        return err
    try:
        payload = {"networks": [network], "text": text, "publishDate": publish_date}
        if image_url:
            payload["mediaList"] = [{"url": image_url}]
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{BASE_URL}/blogs/{blog_id}/posts", headers=_headers(), json=payload)
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_analytics")
async def get_analytics(blog_id: int, network: str, init_date: str, end_date: str) -> str:
    """Get analytics. Dates: YYYY-MM-DD"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f"{BASE_URL}/blogs/{blog_id}/analytics/{network}",
                headers=_headers(),
                params={"initDate": init_date, "endDate": end_date},
            )
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_linkedin_posts")
async def get_linkedin_posts(blog_id: int, init_date: str, end_date: str) -> str:
    """Get published LinkedIn posts. Dates: YYYY-MM-DD"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs/{blog_id}/posts/linkedin", headers=_headers(), params={"initDate": init_date, "endDate": end_date})
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_instagram_posts")
async def get_instagram_posts(blog_id: int, init_date: str, end_date: str) -> str:
    """Get published Instagram posts. Dates: YYYY-MM-DD"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs/{blog_id}/posts/instagram", headers=_headers(), params={"initDate": init_date, "endDate": end_date})
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

@mcp.tool(name="get_facebook_posts")
async def get_facebook_posts(blog_id: int, init_date: str, end_date: str) -> str:
    """Get published Facebook posts. Dates: YYYY-MM-DD"""
    err = _check_key()
    if err:
        return err
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{BASE_URL}/blogs/{blog_id}/posts/facebook", headers=_headers(), params={"initDate": init_date, "endDate": end_date})
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return _handle_error(e)

if __name__ == "__main__":
    from mcp.server.transport_security import TransportSecuritySettings
    port = int(os.environ.get("PORT", 8000))
    mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
