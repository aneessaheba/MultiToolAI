"""
Tools for Multi-Agent System
"""

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import wikipedia
from langchain.agents import tool
from googlesearch import search
from bs4 import BeautifulSoup
from dotenv import load_dotenv


import chromadb
from chromadb.config import Settings
from datetime import datetime
import uuid


load_dotenv()

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

# WIKIPEDIA SEARCH TOOL

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

# GOOGLE SEARCH TOOL

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

# WEB SCRAPER TOOL

@tool
def web_scraper(url: str) -> str:
    """
    Fetches and extracts text content from a web page.
    Use this to read articles, blog posts, or get content from a specific URL.
    
    Args:
        url: The web page URL to scrape (e.g., "https://example.com/article")
    
    Example: web_scraper("https://en.wikipedia.org/wiki/Python")
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        # Limit to first 1000 characters
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text
    
    except Exception as e:
        raise ValueError(f"Failed to scrape URL: {str(e)}")

# EMAIL TOOL

@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient.
    Use this when user asks to send an email or mail results.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body content
    
    Example: send_email("user@example.com", "Test", "Hello World")
    """
    try:
        from_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        
        if not from_email or not password:
            return "Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file"
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        
        return f"Email sent successfully to {to_email}"
    
    except Exception as e:
        raise ValueError(f"Failed to send email: {str(e)}")

# SUMMARIZER TOOL

@tool
def summarize_text(text: str) -> str:
    """
    Summarize long text into key points.
    Use this to condense articles, documents, or long content.
    
    Args:
        text: The text to summarize
    
    Example: summarize_text("Long article text here...")
    """
    try:
        # Simple summarization: take first 3 sentences and last sentence
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text
        
        summary = '. '.join(sentences[:3] + [sentences[-1]]) + '.'
        return f"Summary: {summary}"
    
    except Exception as e:
        raise ValueError(f"Summarization failed: {str(e)}")


# MEMORY MANAGEMENT SYSTEM WITH CHROMADB

# This class manages semantic memory using ChromaDB vector database
# - Stores memories with automatic embeddings for semantic search
# - Persists data to disk (survives restarts)
# - Uses cosine similarity to find related memories


class MemoryManager:
    """Manages semantic memory storage and retrieval using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_memory"):
        """
        Initialize ChromaDB with persistent storage
        
        NEW: Creates a local vector database that:
        - Stores memories as embeddings (vectors)
        - Persists to ./chroma_memory folder
        - Automatically loads existing memories on restart
        """
        
        # NEW: Create persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # NEW: Get or create collection (like a table in a database)
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Agent's semantic memory storage"}
        )
        
        print(f"✓ Memory initialized. Current memories: {self.collection.count()}")
    
    def store(self, content: str, metadata: dict = None) -> str:
        """
        NEW: Store a memory with automatic embedding
        
        ChromaDB automatically:
        1. Converts text to embeddings (vectors)
        2. Stores embeddings for semantic search
        3. Saves to disk for persistence
        
        Args:
            content: The memory text to store
            metadata: Optional tags/categories
        
        Returns:
            Memory ID (UUID)
        """
        memory_id = str(uuid.uuid4())  # NEW: Unique ID for each memory
        timestamp = datetime.now().isoformat()
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": timestamp,
            "memory_id": memory_id
        })
        
        # NEW: ChromaDB automatically creates embeddings and stores them
        self.collection.add(
            documents=[content],      # Text to store
            metadatas=[metadata],      # Tags/timestamp
            ids=[memory_id]            # Unique identifier
        )
        
        return memory_id
    
    def recall(self, query: str, n_results: int = 3) -> list:
        """
        NEW: Recall memories using SEMANTIC SEARCH
        
        How it works:
        1. Converts query to embedding vector
        2. Finds similar memory vectors using cosine similarity
        3. Returns most relevant memories (not just exact matches!)
        
        Example:
        - Stored: "I love pepperoni pizza"
        - Query: "favorite food" <- Different words!
        - Result: Finds the pizza memory semantically
        
        Args:
            query: What to search for
            n_results: Number of memories to return
        
        Returns:
            List of relevant memories with similarity scores
        """
        if self.collection.count() == 0:
            return []
        
        # NEW: Semantic search using vector similarity
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        
        # Format results
        memories = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "similarity": 1 - results['distances'][0][i] if results['distances'] else 0
                }
                memories.append(memory)
        
        return memories
    
    def get_all_memories(self) -> list:
        """NEW: Get all stored memories"""
        if self.collection.count() == 0:
            return []
        
        results = self.collection.get()
        
        memories = []
        for i, doc in enumerate(results['documents']):
            memory = {
                "content": doc,
                "metadata": results['metadatas'][i] if results['metadatas'] else {},
                "id": results['ids'][i]
            }
            memories.append(memory)
        
        return memories
    
    def clear_all(self) -> int:
        """NEW: Clear all memories and return count of deleted memories"""
        count = self.collection.count()
        self.client.delete_collection("agent_memory")
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Agent's semantic memory storage"}
        )
        return count

# NEW: Initialize global memory manager (singleton pattern)
memory_manager = MemoryManager()


# MEMORY TOOLS - LangChain Tool Wrappers


@tool
def store_memory(content: str, tags: str = "") -> str:
    """
    NEW TOOL: Store information in long-term memory.
    Use this when the user asks you to remember something.
    
    Features:
    - Stores with timestamp
    - Optional tags for categorization
    - Persistent (survives restart)
    - Automatically creates embeddings for semantic search
    
    Args:
        content: The information to remember (e.g., "User loves pepperoni pizza")
        tags: Optional comma-separated tags (e.g., "food,preferences")
    
    Examples:
        - store_memory("User's favorite color is blue", "preferences,color")
        - store_memory("Meeting with John scheduled for next Monday at 3pm", "schedule,meetings")
        - store_memory("User allergic to peanuts", "health,allergies")
    """
    try:
        metadata = {}
        if tags:
            metadata["tags"] = tags
        
        memory_id = memory_manager.store(content, metadata)
        return f"✓ Memory stored successfully! I'll remember: '{content}'"
    
    except Exception as e:
        return f"Failed to store memory: {str(e)}"

@tool
def recall_memory(query: str, num_results: int = 3) -> str:
    """
    NEW TOOL: Search and recall memories using SEMANTIC SEARCH.
    Use this when the user asks you to remember or recall something.
    
    How it's different from keyword search:
    - Finds semantically similar memories (not just exact matches)
    - "favorite food" will find "loves pizza" 
    - "health issues" will find "allergic to peanuts"
    
    Args:
        query: What to search for (e.g., "food preferences", "meetings", "what I said about vacation")
        num_results: Number of memories to retrieve (default: 3)
    
    Examples:
        - recall_memory("What did I say about food?")
        - recall_memory("My schedule")
        - recall_memory("health information")
    """
    try:
        memories = memory_manager.recall(query, num_results)
        
        if not memories:
            return "No memories found related to your query."
        
        response = f"I found {len(memories)} relevant memories:\n\n"
        
        for i, memory in enumerate(memories, 1):
            content = memory['content']
            timestamp = memory['metadata'].get('timestamp', 'Unknown time')
            tags = memory['metadata'].get('tags', '')
            
            response += f"{i}. {content}\n"
            response += f"   (Stored: {timestamp[:10]}"
            if tags:
                response += f", Tags: {tags}"
            response += ")\n\n"
        
        return response.strip()
    
    except Exception as e:
        return f"Failed to recall memories: {str(e)}"

@tool
def list_all_memories() -> str:
    """
    NEW TOOL: List all stored memories.
    Use this when the user wants to see everything you remember.
    
    Example: "Show me all my memories" or "What do you remember about me?"
    """
    try:
        memories = memory_manager.get_all_memories()
        
        if not memories:
            return "I don't have any memories stored yet."
        
        response = f"I have {len(memories)} memories stored:\n\n"
        
        for i, memory in enumerate(memories, 1):
            content = memory['content']
            timestamp = memory['metadata'].get('timestamp', 'Unknown')
            
            response += f"{i}. {content}\n"
            response += f"   (Stored: {timestamp[:10]})\n\n"
        
        return response.strip()
    
    except Exception as e:
        return f"Failed to list memories: {str(e)}"

@tool
def clear_all_memories() -> str:
    """
    NEW TOOL: Delete all stored memories.
    Use this ONLY when the user explicitly asks to forget everything or clear all memories.
    
    Example: "Forget everything" or "Clear all my memories"
    """
    try:
        count = memory_manager.clear_all()
        return f"✓ Cleared {count} memories. My memory is now empty."
    
    except Exception as e:
        return f"Failed to clear memories: {str(e)}"


ALL_TOOLS = [
    
    calculator, 
    get_weather, 
    search_wikipedia, 
    google_search, 
    web_scraper, 
    send_email, 
    summarize_text,
    
    #  Memory tools
    store_memory,          # Store new memories
    recall_memory,         # Semantic search in memories
    list_all_memories,     # List all memories
    clear_all_memories     # Clear all memories
]