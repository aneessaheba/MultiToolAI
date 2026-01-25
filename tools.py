"""
Tools for Multi-Agent System
"""

from langchain.agents import tool

# CALCULATOR TOOL

@tool
def calculator(expression: str) -> float:
    """
    Evaluates mathematical expressions.
    Use this for any math calculations like addition, subtraction, multiplication, division.
    Example: calculator("5 + 3") returns 8
    """
    try:
        # Safety check
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters in expression")
        
        result = eval(expression)
        return result
    
    except Exception as e:
        raise ValueError(f"Calculation error: {str(e)}")