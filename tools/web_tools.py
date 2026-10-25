"""
Web search and URL content fetching tools for JARVIS.
"""

import urllib.request
import re
from typing import Optional


def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for real-time information, documentation, news, or answers.
    
    Args:
        query: Search keywords or question.
        max_results: Number of search results to return.
    """
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"No web search results found for '{query}'."

        formatted = [f"Search Results for '{query}':\n"]
        for idx, r in enumerate(results, 1):
            title = r.get("title", "No Title")
            href = r.get("href", "")
            body = r.get("body", "")
            formatted.append(f"{idx}. {title}\n   URL: {href}\n   Snippet: {body}\n")

        return "\n".join(formatted)
    except Exception as e:
        # Fallback if duckduckgo_search encounters rate limits
        return f"Web search note: Unable to fetch external search results ({str(e)})."


def fetch_url(url: str, max_length: int = 4000) -> str:
    """
    Fetch the text content of a webpage given its URL.
    
    Args:
        url: Full URL starting with http:// or https://
        max_length: Maximum characters of text to return.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")

        # Strip scripts, styles, and HTML tags
        cleaned = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<style.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', cleaned)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) > max_length:
            return text[:max_length] + f"\n\n... (Page content truncated to {max_length} characters)"
        return text if text else "Page loaded but no readable text was extracted."
    except Exception as e:
        return f"Error fetching URL '{url}': {str(e)}"
