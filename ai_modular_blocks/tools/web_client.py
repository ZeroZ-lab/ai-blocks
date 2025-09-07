"""
Web client tool - Does one thing well: HTTP requests

Simple wrapper around aiohttp, optional dependency.
"""

from typing import Dict, Any, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class WebClient:
    """Simple HTTP client using aiohttp."""
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for WebClient. Install with: pip install aiohttp")
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", url, headers=headers)
    
    async def post(
        self, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", url, data=data, headers=headers)

    async def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Alias for GET to match example usage."""
        return await self.get(url, headers=headers)
    
    async def _request(
        self, 
        method: str, 
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request."""
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Reasonable default headers to avoid 403 from some sites
                default_headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Connection": "keep-alive",
                }

                kwargs = {}
                if data:
                    kwargs['json'] = data
                all_headers = default_headers.copy()
                if headers:
                    all_headers.update(headers)
                kwargs['headers'] = all_headers
                
                async with session.request(method, url, **kwargs) as response:
                    response_text = await response.text()

                    # Try to parse as JSON
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = None

                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "content": response_text,
                        "url": str(response.url),
                        "success": 200 <= response.status < 300,
                    }
                    
        except Exception as e:
            return {
                "error": str(e),
                "url": url,
                "method": method,
                "success": False
            }


# Direct usage:
# client = WebClient()
# result = await client.get("https://api.github.com/users/octocat")
# print(result["data"]["name"])  # "The Octocat"
