"""
Tools for Multi-Agent System
"""

import requests
import wikipedia  # NEW: Added for Wikipedia search
from langchain.agents import tool
from googlesearch import search  # NEW: Added for Google search

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

# WEATHER TOOL

@tool
def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    Use this when user asks about weather, temperature, or climate.
    
    Args:
        city: Name of the city (e.g., "London", "San Jose")
    
    Example: get_weather("San Jose")
    """
    try:
        url = f"http://wttr.in/{city}?format=%C+%t"
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.text.strip()
        return f"Weather in {city}: {result}"
    
    except Exception as e:
        raise ValueError(f"Failed to get weather: {str(e)}")

# WIKIPEDIA SEARCH TOOL - NEW

@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia and get a summary.
    Use this when user asks about facts, people, places, history, or general knowledge.
    
    Args:
        query: Search term (e.g., "Albert Einstein", "Python programming")
    
    Example: search_wikipedia("Eiffel Tower")
    """
    try:
        result = wikipedia.summary(query, sentences=3)
        return result
    
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found. Please be more specific. Options: {', '.join(e.options[:5])}"
    
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'"
    
    except Exception as e:
        raise ValueError(f"Wikipedia search failed: {str(e)}")

# GOOGLE SEARCH TOOL - NEW

@tool
def google_search(query: str) -> str:
    """
    Search Google and return top results.
    Use this when user asks to search the web or find current information.
    
    Args:
        query: Search query (e.g., "latest news on AI", "best restaurants in NYC")
    
    Example: google_search("Python tutorials")
    """
    try:
        results = []
        for url in search(query, num_results=5):
            results.append(url)
        
        if not results:
            return f"No results found for '{query}'"
        
        output = f"Top Google search results for '{query}':\n"
        for i, url in enumerate(results, 1):
            output += f"{i}. {url}\n"
        
        return output
    
    except Exception as e:
        raise ValueError(f"Google search failed: {str(e)}")
    
    

# Export all tools
ALL_TOOLS = [calculator, get_weather, search_wikipedia, google_search]  # NEW: Added google_search