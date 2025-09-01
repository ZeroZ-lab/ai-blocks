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
                kwargs = {}
                if data:
                    kwargs['json'] = data
                if headers:
                    kwargs['headers'] = headers
                
                async with session.request(method, url, **kwargs) as response:
                    response_text = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        response_data = await response.json()
                    except:
                        response_data = response_text
                    
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "url": str(response.url),
                        "success": 200 <= response.status < 300
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