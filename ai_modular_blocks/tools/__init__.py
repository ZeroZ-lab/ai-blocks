"""
Modular tools - Each tool is independent and does one thing well

Import only what you need:
    from ai_modular_blocks.tools import Calculator
    from ai_modular_blocks.tools import FileOperations  
    from ai_modular_blocks.tools import WebClient

Or use the optional convenience wrapper:
    from ai_modular_blocks.tools import ToolBox
"""

from .calculator import Calculator
from .file_ops import FileOperations

# Optional imports with graceful fallback
try:
    from .web_client import WebClient
    WEB_CLIENT_AVAILABLE = True
except ImportError:
    WebClient = None
    WEB_CLIENT_AVAILABLE = False


class ToolBox:
    """
    Optional convenience wrapper for tools.
    
    Users can use this or directly instantiate individual tools.
    Pure composition, no magic.
    """
    
    def __init__(self):
        self.calculator = Calculator()
        self.files = FileOperations()
        
        if WEB_CLIENT_AVAILABLE:
            self.web = WebClient()
        else:
            self.web = None
    
    async def calculate(self, expression: str):
        """Convenience method for calculator."""
        return self.calculator.calculate(expression)
    
    async def read_file(self, file_path: str):
        """Convenience method for file reading."""
        return self.files.read_file(file_path)
    
    async def write_file(self, file_path: str, content: str):
        """Convenience method for file writing."""
        return self.files.write_file(file_path, content)
    
    async def http_get(self, url: str):
        """Convenience method for HTTP GET."""
        if self.web is None:
            return {"error": "WebClient not available. Install aiohttp.", "success": False}
        return await self.web.get(url)


# Users have choices:
#
# Option 1 - Direct tool usage (most flexible):
# calc = Calculator()
# result = calc.calculate("2+2")
#
# Option 2 - Convenience wrapper:
# tools = ToolBox()  
# result = await tools.calculate("2+2")
#
# Option 3 - Custom composition:
# class MyTools:
#     def __init__(self):
#         self.calc = Calculator()
#         self.custom_tool = MyCustomTool()


__all__ = ["Calculator", "FileOperations", "ToolBox"]

if WEB_CLIENT_AVAILABLE:
    __all__.append("WebClient")