"""
Calculator tool - Does one thing well: mathematical calculations

Pure Python, no framework dependencies.
Users can use it directly or through any tool system.
"""

import math
import re
from typing import Dict, Any


class Calculator:
    """Simple calculator that evaluates mathematical expressions safely."""
    
    def __init__(self):
        # Safe mathematical operations
        self.safe_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "len": len,
            # Math functions
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log, "exp": math.exp,
            "pi": math.pi, "e": math.e
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Calculate a mathematical expression safely.
        
        Args:
            expression: Mathematical expression like "2+2*3" or "sqrt(16)"
            
        Returns:
            dict with result and metadata
        """
        try:
            # Security: only allow safe operations
            if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', expression):
                # Contains function calls, check they're safe
                allowed_pattern = r'^[0-9+\-*/().\s' + ''.join(self.safe_names.keys()) + r']+$'
                if not re.match(allowed_pattern, expression.replace(' ', '')):
                    raise ValueError("Unsafe expression")
            
            # Evaluate with safe environment
            result = eval(expression, {"__builtins__": {}}, self.safe_names)
            
            return {
                "result": result,
                "expression": expression,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression,
                "success": False
            }


# Direct usage (no framework needed):
# calc = Calculator()
# result = calc.calculate("2+2*3")
# print(result["result"])  # 8